from ai_os.brain.provider_brain import ProviderBrain


class GeminiBrain(ProviderBrain):
    """
    Backwards-compatible alias kept for older imports.
    This no longer calls Gemini directly.
    """

    name = "CloudFallback"
