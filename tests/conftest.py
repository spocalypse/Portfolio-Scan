"""Shared test doubles. No test in this suite ever holds a real ANTHROPIC_API_KEY or
makes a network call — CI runs entirely offline (see .github/workflows/ci.yml)."""

from types import SimpleNamespace


class FakeAnthropicClient:
    """Stands in for anthropic.Anthropic. Each entry in `responses` is consumed, in
    order, by one `messages.create` call — a dict becomes a tool_use block's `.input`;
    None simulates a model turn that never called the tool.
    """

    def __init__(self, responses: list[dict | None]):
        self._responses = list(responses)
        self.calls: list[dict] = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        tool_input = self._responses.pop(0)
        if tool_input is None:
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text="(no tool call)")]
            )
        return SimpleNamespace(
            content=[SimpleNamespace(type="tool_use", input=tool_input)]
        )
