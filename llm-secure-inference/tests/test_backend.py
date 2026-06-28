import pytest

from inference.backend import EchoBackend


@pytest.mark.asyncio
async def test_echo_backend_truncates_to_max_tokens() -> None:
    completion = await EchoBackend().complete("one two three four", max_tokens=2)
    assert completion.text == "one two"
    assert completion.tokens == 2
