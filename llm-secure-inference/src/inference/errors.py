class InferenceError(Exception):
    pass


class SecretNotFoundError(InferenceError):
    pass


class RateLimitExceededError(InferenceError):
    pass
