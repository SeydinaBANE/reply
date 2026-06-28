class MappingGenerator:
    def __init__(self, mapping: dict[str, str]) -> None:
        self._mapping = mapping

    def generate(self, prompt: str) -> str:
        return self._mapping.get(prompt, "")
