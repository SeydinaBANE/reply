class PipelineError(Exception):
    pass


class RegistryError(PipelineError):
    pass


class EvaluationGateError(PipelineError):
    pass


class InvalidDatasetError(PipelineError):
    pass
