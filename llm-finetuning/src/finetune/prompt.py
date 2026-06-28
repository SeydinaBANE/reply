_TEMPLATE = "### Instruction:\n{instruction}\n\n### Response:\n"


def format_prompt(instruction: str) -> str:
    return _TEMPLATE.format(instruction=instruction)
