"""
Simple TTS implementation using Windows SAPI for testing
"""
import asyncio
import tempfile
import os
import wave
import numpy as np
from livekit.agents import tts
from livekit import rtc

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class SimpleTTS(tts.TTS):
    def __init__(self):
        super().__init__(
            capabilities=tts.TTSCapabilities(
                streaming=False,
            ),
            sample_rate=16000,
            num_channels=1,
        )
        if PYTTSX3_AVAILABLE:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', 150)  # Speed
            self._engine.setProperty('volume', 0.9)  # Volume
        else:
            self._engine = None

    def synthesize(self, text: str) -> "SimpleSynthesizeStream":
        return SimpleSynthesizeStream(text, self._engine, self._sample_rate)

class SimpleSynthesizeStream(tts.SynthesizeStream):
    def __init__(self, text: str, engine, sample_rate: int):
        super().__init__()
        self._text = text
        self._engine = engine
        self._sample_rate = sample_rate
        self._done = False

    async def __anext__(self) -> rtc.AudioFrame:
        if self._done:
            raise StopAsyncIteration

        self._done = True
        
        if not self._engine:
            # Fallback: create silence
            duration = len(self._text) * 0.1  # Rough estimate
            samples = int(duration * self._sample_rate)
            audio_data = np.zeros(samples, dtype=np.int16)
        else:
            # Use pyttsx3 to generate audio
            try:
                # Save to temporary file
                temp_file = "temp_tts.wav"
                self._engine.save_to_file(self._text, temp_file)
                self._engine.runAndWait()
                
                # Read the audio file
                with wave.open(temp_file, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Clean up
                import os
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            except Exception as e:
                print(f"TTS Error: {e}")
                # Fallback to silence
                duration = len(self._text) * 0.1
                samples = int(duration * self._sample_rate)
                audio_data = np.zeros(samples, dtype=np.int16)

        # Create audio frame
        audio_frame = rtc.AudioFrame(
            data=audio_data.tobytes(),
            sample_rate=self._sample_rate,
            num_channels=1,
            samples_per_channel=len(audio_data),
        )
        
        return audio_frame
