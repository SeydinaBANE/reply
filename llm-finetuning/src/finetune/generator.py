import logging

from finetune.errors import FinetuneError

logger = logging.getLogger(__name__)


class VertexTextGenerator:
    def __init__(self, project: str, location: str, model: str) -> None:
        self._project = project
        self._location = location
        self._model = model

    def generate(self, prompt: str) -> str:
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=self._project, location=self._location)
            response = GenerativeModel(self._model).generate_content(prompt)
        except Exception as exc:
            raise FinetuneError(str(exc)) from exc
        return str(response.text)
