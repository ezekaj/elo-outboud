"""
LM Studio LLM integration for LiveKit Agents
Uses OpenAI-compatible API to connect to local LM Studio instance
"""
import asyncio
import json
from typing import AsyncIterator, List, Optional, Union
import httpx
from livekit.agents import llm
from livekit.agents._exceptions import APIConnectionError, APIStatusError
from config import settings
from logging_config import agent_logger


class LMStudioLLM(llm.LLM):
    """LM Studio LLM implementation using OpenAI-compatible API"""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "local-model",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: float = 30.0,
    ):
        self._api_key = api_key or settings.lm_studio_api_key
        self._base_url = base_url or settings.lm_studio_base_url
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout
        
        # Ensure base_url ends with /v1 if not already
        if not self._base_url.endswith('/v1'):
            self._base_url = self._base_url.rstrip('/') + '/v1'
    
    async def _check_lm_studio_connection(self) -> bool:
        """Check if LM Studio is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/models")
                return response.status_code == 200
        except Exception as e:
            agent_logger.logger.warning(f"LM Studio connection check failed: {e}")
            return False
    
    async def _make_request(self, messages: List[dict], stream: bool = False) -> Union[dict, AsyncIterator[dict]]:
        """Make request to LM Studio API"""
        
        # Check if LM Studio is running
        if not await self._check_lm_studio_connection():
            raise APIConnectionError("LM Studio is not running or not accessible at " + self._base_url)
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": stream
        }
        
        url = f"{self._base_url}/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                if stream:
                    return self._stream_response(client, url, headers, payload)
                else:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    return response.json()
        except httpx.HTTPStatusError as e:
            raise APIStatusError(f"LM Studio API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise APIConnectionError(f"Failed to connect to LM Studio: {e}")
    
    async def _stream_response(self, client: httpx.AsyncClient, url: str, headers: dict, payload: dict) -> AsyncIterator[dict]:
        """Stream response from LM Studio"""
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        continue
    
    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        conn_options: llm.LLMOptions = llm.LLMOptions(),
        fnc_ctx: Optional[llm.FunctionContext] = None,
    ) -> "LMStudioLLMStream":
        return LMStudioLLMStream(
            llm=self,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            fnc_ctx=fnc_ctx,
        )


class LMStudioLLMStream(llm.LLMStream):
    """LM Studio LLM stream implementation"""
    
    def __init__(
        self,
        *,
        llm: LMStudioLLM,
        chat_ctx: llm.ChatContext,
        conn_options: llm.LLMOptions,
        fnc_ctx: Optional[llm.FunctionContext],
    ):
        super().__init__(
            llm=llm,
            chat_ctx=chat_ctx,
            conn_options=conn_options,
            fnc_ctx=fnc_ctx,
        )
        self._llm = llm
    
    async def _run(self) -> AsyncIterator[llm.ChatChunk]:
        """Run the LLM stream"""
        
        # Convert chat context to messages format
        messages = []
        for msg in self._chat_ctx.messages:
            if isinstance(msg, llm.ChatMessage):
                role = "user" if msg.role == llm.ChatRole.USER else "assistant"
                if msg.role == llm.ChatRole.SYSTEM:
                    role = "system"
                messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        try:
            # Use streaming for real-time response
            stream = await self._llm._make_request(messages, stream=True)
            
            async for chunk in stream:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    choice = chunk["choices"][0]
                    if "delta" in choice and "content" in choice["delta"]:
                        content = choice["delta"]["content"]
                        if content:
                            yield llm.ChatChunk(
                                choices=[
                                    llm.Choice(
                                        delta=llm.ChoiceDelta(
                                            content=content,
                                            role=llm.ChatRole.ASSISTANT,
                                        )
                                    )
                                ]
                            )
            
            # Mark stream as finished
            yield llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChoiceDelta(
                            content="",
                            role=llm.ChatRole.ASSISTANT,
                        ),
                        finish_reason="stop",
                    )
                ]
            )
            
        except Exception as e:
            agent_logger.logger.error(f"LM Studio stream error: {e}")
            # Fallback response if LM Studio fails
            fallback_msg = "I apologize, but I'm having trouble connecting to my AI system. However, I can still help you with basic information about our dental services. How can I assist you today?"
            yield llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChoiceDelta(
                            content=fallback_msg,
                            role=llm.ChatRole.ASSISTANT,
                        ),
                        finish_reason="stop",
                    )
                ]
            )