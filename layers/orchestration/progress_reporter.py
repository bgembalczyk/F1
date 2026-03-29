from __future__ import annotations


class ProgressReporter:
    """Unified progress messages for orchestration jobs."""

    _TEMPLATES: dict[str, dict[str, str]] = {
        "list": {
            "started": "[list] running  {name}",
            "finished": "[list] finished {name}",
            "skipped": "[list] skipped  {name}: {reason}",
        },
        "complete": {
            "started": "[complete] running  {name}",
            "finished": "[complete] finished {name}",
            "skipped": "[complete] skipped  {name}: {reason}",
        },
        "main": {
            "started": "[main] running  {name}",
            "finished": "[main] finished {name}",
            "skipped": "[main] skipped  {name}: {reason}",
        },
    }

    def job_started(self, kind: str, name: str) -> None:
        print(self._render(kind=kind, state="started", name=name))

    def job_finished(self, kind: str, name: str) -> None:
        print(self._render(kind=kind, state="finished", name=name))

    def job_skipped(self, kind: str, name: str, reason: str) -> None:
        print(self._render(kind=kind, state="skipped", name=name, reason=reason))

    def _render(self, *, kind: str, state: str, name: str, reason: str = "") -> str:
        kind_templates = self._TEMPLATES.get(kind, self._TEMPLATES["main"])
        template = kind_templates[state]
        return template.format(name=name, reason=reason)
