from __future__ import annotations

import sys
from typing import TextIO

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)


class ProgressBar:
    """Terminal progress bar backed by ``rich.progress``.

    The bar starts disabled (``total=0``). The real total arrives later, once
    the CLI has discovered how many tables to profile, so :meth:`start` and
    :meth:`update` accept it lazily and (re)build the live display on demand.
    When the stream is not a TTY the bar stays a no-op so non-interactive runs
    (pipes, CI logs) stay quiet.
    """

    def __init__(self, label: str, total: int, stream: TextIO | None = None) -> None:
        self.label = label
        self.stream = stream or sys.stderr
        self.total = total
        self.current = 0
        self.item = ""
        self._task_id: int | None = None
        self._progress: Progress | None = None
        if total > 0 and self.stream.isatty():
            self._build()

    def _build(self) -> Progress:
        progress = Progress(
            TextColumn("[bold blue]{task.fields[label]}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            TextColumn("{task.fields[item]}"),
            console=Console(file=self.stream),
            transient=True,
        )
        self._progress = progress
        return progress

    @property
    def enabled(self) -> bool:
        """True once the bar is (or can be) shown on an interactive stream."""
        return self._progress is not None or (
            self.total <= 0 and self.stream.isatty()
        )

    def start(self, item: str = "") -> None:
        self.current = 0
        self.item = item
        if self.total <= 0 or not self.stream.isatty():
            return
        if self._progress is None:
            self._build()
        assert self._progress is not None
        self._progress.start()
        self._task_id = self._progress.add_task(
            self.label, total=self.total, label=self.label, item=item
        )

    def update(self, current: int, item: str = "") -> None:
        if self._progress is None or self._task_id is None:
            return
        self.current = min(max(current, 0), self.total)
        self.item = item
        self._progress.update(
            self._task_id, completed=self.current, total=self.total, item=item
        )

    def advance(self, item: str = "") -> None:
        self.update(self.current + 1, item)

    def finish(self, message: str | None = None) -> None:
        if self._progress is not None:
            self._progress.stop()
            self._task_id = None
        if message:
            self.stream.write(f"{message}\n")
            self.stream.flush()
