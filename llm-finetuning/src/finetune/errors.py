class FinetuneError(Exception):
    pass


class InvalidDatasetError(FinetuneError):
    pass


class EvaluationBaselineError(FinetuneError):
    pass
