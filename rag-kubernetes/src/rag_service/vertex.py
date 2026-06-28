import logging

from rag_service.errors import EmbeddingError, GenerationError

logger = logging.getLogger(__name__)


class VertexEmbeddingBackend:
    def __init__(self, project: str, location: str, model: str) -> None:
        self._project = project
        self._location = location
        self._model = model

    async def embed(self, text: str) -> list[float]:
        try:
            import vertexai
            from vertexai.language_models import TextEmbeddingModel

            vertexai.init(project=self._project, location=self._location)
            model = TextEmbeddingModel.from_pretrained(self._model)
            embeddings = model.get_embeddings([text])
        except Exception as exc:
            raise EmbeddingError(str(exc)) from exc
        return list(embeddings[0].values)


class VertexGenerator:
    def __init__(self, project: str, location: str, model: str) -> None:
        self._project = project
        self._location = location
        self._model = model

    async def generate(self, prompt: str) -> str:
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=self._project, location=self._location)
            model = GenerativeModel(self._model)
            response = model.generate_content(prompt)
        except Exception as exc:
            raise GenerationError(str(exc)) from exc
        return str(response.text)
