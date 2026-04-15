from ai_os.brain.provider_brain import ProviderBrain

provider_brain = ProviderBrain()


def choose_brain(intent: dict):
    """
    All AI requests flow through the shared provider abstraction so model
    routing, Ollama detection, and fallback remain centralized.
    """

    return provider_brain
