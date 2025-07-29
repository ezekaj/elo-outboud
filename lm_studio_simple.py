"""
Simple LM Studio integration using OpenAI plugin as base
"""
import httpx
import asyncio
from livekit.plugins import openai as livekit_openai
from config import settings
from logging_config import agent_logger


def create_lm_studio_llm():
    """Create LM Studio LLM using OpenAI plugin with custom base URL"""
    try:
        # Test LM Studio connection first
        response = httpx.get(f"{settings.lm_studio_base_url}/models", timeout=5.0)
        if response.status_code == 200:
            agent_logger.logger.info("LM Studio detected, using local AI")
            
            # Use OpenAI plugin but point to LM Studio
            return livekit_openai.LLM(
                api_key=settings.lm_studio_api_key,
                base_url=settings.lm_studio_base_url,
                model="local-model",
                temperature=0.7,
            )
        else:
            raise Exception("LM Studio not accessible")
            
    except Exception as e:
        agent_logger.logger.warning(f"LM Studio not available ({e}), falling back to simple responses")
        
        # Return a simple fallback LLM that gives basic responses
        return SimpleFallbackLLM()


class SimpleFallbackLLM:
    """Simple fallback when LM Studio is not available"""
    
    def __init__(self):
        self.responses = {
            "greeting": "Hello! I'm Elo, your dental assistant from Romi Dental Clinic. How can I help you today?",
            "appointment": "I'd be happy to help you schedule an appointment. Let me check our available times for you.",
            "services": "We offer comprehensive dental services including cleanings, cosmetic dentistry, emergency care, and more. What service interests you?",
            "default": "I apologize, but I'm experiencing some technical difficulties with my AI system. However, I can still help you with basic information about our dental services. Please call our clinic directly for immediate assistance."
        }
    
    def chat(self, *, chat_ctx, conn_options=None, fnc_ctx=None):
        return SimpleFallbackStream(self.responses)


class SimpleFallbackStream:
    """Simple stream that provides fallback responses"""
    
    def __init__(self, responses):
        self.responses = responses
    
    async def __aiter__(self):
        # Determine response based on context
        response = self.responses["default"]
        
        # Simple keyword-based response selection
        # In a real implementation, you'd analyze the chat context
        # For now, just return a helpful default message
        
        yield MockChatChunk(content=response)
    
    def __aiter__(self):
        return self.__aiter__()


class MockChatChunk:
    """Mock chat chunk for fallback responses"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice for fallback responses"""
    def __init__(self, content):
        self.delta = MockDelta(content)


class MockDelta:
    """Mock delta for fallback responses"""
    def __init__(self, content):
        self.content = content