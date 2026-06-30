class InferenceError(Exception):
    pass


class SecretNotFoundError(InferenceError):
    pass


class RateLimitExceededError(InferenceError):
    pass


class RateLimiterUnavailableError(InferenceError):
    pass


class UnauthorizedError(InferenceError):
    pass


class BackendError(InferenceError):
    pass
