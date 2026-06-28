class RagError(Exception):
    pass


class EmptyCorpusError(RagError):
    pass


class EmbeddingError(RagError):
    pass


class GenerationError(RagError):
    pass
