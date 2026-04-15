import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional

import requests
from dotenv import load_dotenv


load_dotenv()


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_API_KEY = "ollama"
DEFAULT_OLLAMA_CHAT_MODEL = "llama3"
DEFAULT_OLLAMA_CODE_MODEL = "codellama"
DEFAULT_OLLAMA_AGENT_MODEL = "codellama"


class AIProviderError(RuntimeError):
    """Raised when the configured AI provider cannot serve a request."""


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProviderSettings:
    use_ollama: bool = _env_flag("USE_OLLAMA", True)
    enable_fallback: bool = _env_flag("AI_ENABLE_FALLBACK", True)
    timeout_seconds: float = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    ollama_api_key: str = os.getenv("OLLAMA_API_KEY", DEFAULT_OLLAMA_API_KEY)
    ollama_model: str = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_CHAT_MODEL)
    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_CHAT_MODEL))
    ollama_code_model: str = os.getenv("OLLAMA_CODE_MODEL", os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_CODE_MODEL))
    ollama_agent_model: str = os.getenv("OLLAMA_AGENT_MODEL", os.getenv("OLLAMA_CODE_MODEL", os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_AGENT_MODEL)))

    cloud_base_url: str = os.getenv("CLOUD_API_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    cloud_api_key: str = os.getenv("CLOUD_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    cloud_model: str = os.getenv("CLOUD_MODEL", "gpt-4o-mini")
    cloud_chat_model: str = os.getenv("CLOUD_CHAT_MODEL", os.getenv("CLOUD_MODEL", "gpt-4o-mini"))
    cloud_code_model: str = os.getenv("CLOUD_CODE_MODEL", os.getenv("CLOUD_MODEL", "gpt-4o-mini"))
    cloud_agent_model: str = os.getenv("CLOUD_AGENT_MODEL", os.getenv("CLOUD_CODE_MODEL", os.getenv("CLOUD_MODEL", "gpt-4o-mini")))


class AIProvider:
    """
    OpenAI-compatible provider wrapper.

    By default it targets the local Ollama endpoint and can fall back to a
    cloud OpenAI-compatible API when configured.
    """

    def __init__(self, settings: Optional[ProviderSettings] = None):
        self.settings = settings or ProviderSettings()
        self.session = requests.Session()

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        messages = self._build_messages(prompt, system_prompt)
        return self.chat(
            messages,
            model=model,
            purpose="chat",
            temperature=temperature,
            stream=stream,
        )

    def generate_code(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.1,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        messages = self._build_messages(prompt, system_prompt)
        return self.chat(
            messages,
            model=model,
            purpose="code",
            temperature=temperature,
            stream=stream,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        model: Optional[str] = None,
        purpose: str = "chat",
        temperature: float = 0.2,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        request = {
            "messages": messages,
            "model": model or self._resolve_model(purpose, prefer_ollama=self.settings.use_ollama),
            "temperature": temperature,
            "stream": stream,
        }

        if self.settings.use_ollama:
            try:
                request["model"] = self.ensure_ollama_ready(model_name=request["model"]) or request["model"]
                return self._request("ollama", request)
            except Exception as exc:
                if not self._should_fallback():
                    raise self._to_provider_error(exc)
                return self._request_with_fallback(request, exc, purpose)

        return self._request("cloud", request)

    def ensure_ollama_ready(self, model_name: Optional[str] = None) -> Optional[str]:
        """
        Checks the OpenAI-compatible `/models` route so startup failures are
        caught before a full generation request.
        """

        url = f"{self.settings.ollama_base_url}/models"
        try:
            response = self.session.get(
                url,
                headers=self._headers("ollama"),
                timeout=min(self.settings.timeout_seconds, 10),
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise AIProviderError(
                "Ollama is not reachable at "
                f"{self.settings.ollama_base_url}. Start it with `ollama serve` "
                f"and verify the model is available with `ollama pull {model_name or self.settings.ollama_model}`."
            ) from exc

        available_models = {
            item.get("id")
            for item in payload.get("data", [])
            if isinstance(item, dict) and item.get("id")
        }
        if model_name and available_models and model_name not in available_models:
            if ":" not in model_name:
                tagged_match = next(
                    (candidate for candidate in sorted(available_models) if candidate.startswith(f"{model_name}:")),
                    None,
                )
                if tagged_match:
                    return tagged_match
            model_list = ", ".join(sorted(available_models))
            raise AIProviderError(
                f"Ollama is running but model `{model_name}` is missing. "
                f"Pull it with `ollama pull {model_name}` or change `OLLAMA_MODEL`. "
                f"Available models: {model_list}."
            )

        return model_name

    def _request_with_fallback(
        self,
        request: Dict[str, Any],
        original_error: Exception,
        purpose: str,
    ) -> str | Generator[str, None, None]:
        cloud_request = dict(request)
        cloud_request["model"] = self._resolve_model(purpose, prefer_ollama=False)
        try:
            return self._request("cloud", cloud_request)
        except Exception as cloud_exc:
            raise AIProviderError(
                f"Ollama request failed and cloud fallback also failed. "
                f"Ollama error: {original_error}. Cloud error: {cloud_exc}"
            ) from cloud_exc

    def _request(self, provider: str, payload: Dict[str, Any]) -> str | Generator[str, None, None]:
        if provider == "cloud" and not self.settings.cloud_api_key:
            raise AIProviderError(
                "Cloud fallback is enabled but `CLOUD_API_KEY` or `OPENAI_API_KEY` is not set."
            )

        url = f"{self._base_url(provider)}/chat/completions"
        if payload.get("stream"):
            return self._stream_request(url, payload, provider)

        response = self.session.post(
            url,
            headers=self._headers(provider),
            json=payload,
            timeout=self.settings.timeout_seconds,
        )
        self._raise_for_status(response, provider)
        data = response.json()
        return self._extract_text(data)

    def _stream_request(
        self,
        url: str,
        payload: Dict[str, Any],
        provider: str,
    ) -> Generator[str, None, None]:
        response = self.session.post(
            url,
            headers=self._headers(provider),
            json=payload,
            timeout=self.settings.timeout_seconds,
            stream=True,
        )
        self._raise_for_status(response, provider)

        def iterator() -> Generator[str, None, None]:
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = (
                    event.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content")
                )
                if delta:
                    yield delta

        return iterator()

    def _raise_for_status(self, response: requests.Response, provider: str) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = response.text.strip()
            raise AIProviderError(
                f"{provider.capitalize()} AI request failed with status "
                f"{response.status_code}: {detail}"
            ) from exc

    def _extract_text(self, payload: Dict[str, Any]) -> str:
        choices = payload.get("choices", [])
        if not choices:
            raise AIProviderError(f"AI response did not include choices: {payload}")
        message = choices[0].get("message", {})
        content = message.get("content", "")

        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "".join(parts)

        raise AIProviderError(f"Unsupported AI content format: {payload}")

    def _resolve_model(self, purpose: str, *, prefer_ollama: bool) -> str:
        provider_prefix = "ollama" if prefer_ollama else "cloud"
        if purpose == "code":
            return getattr(self.settings, f"{provider_prefix}_code_model")
        if purpose == "agent":
            return getattr(self.settings, f"{provider_prefix}_agent_model")
        return getattr(self.settings, f"{provider_prefix}_chat_model")

    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str],
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _base_url(self, provider: str) -> str:
        return self.settings.ollama_base_url if provider == "ollama" else self.settings.cloud_base_url

    def _headers(self, provider: str) -> Dict[str, str]:
        api_key = self.settings.ollama_api_key if provider == "ollama" else self.settings.cloud_api_key
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _should_fallback(self) -> bool:
        return self.settings.enable_fallback and bool(self.settings.cloud_api_key)

    def _to_provider_error(self, exc: Exception) -> AIProviderError:
        if isinstance(exc, AIProviderError):
            return exc
        return AIProviderError(str(exc))


_provider_instance: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = AIProvider()
    return _provider_instance


def generateText(*args: Any, **kwargs: Any) -> str | Generator[str, None, None]:
    return get_ai_provider().generate_text(*args, **kwargs)


def generateCode(*args: Any, **kwargs: Any) -> str | Generator[str, None, None]:
    return get_ai_provider().generate_code(*args, **kwargs)


def chat(*args: Any, **kwargs: Any) -> str | Generator[str, None, None]:
    return get_ai_provider().chat(*args, **kwargs)
