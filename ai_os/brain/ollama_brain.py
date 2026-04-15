from ai_os.brain.provider_brain import ProviderBrain


class OllamaBrain(ProviderBrain):
    """
    Backwards-compatible alias kept for older imports.
    The actual transport is resolved by `ai_os.ai_provider`.
    """

    name = "Ollama"
