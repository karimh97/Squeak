"""Non-blocking update checks against the public Squeak GitHub releases."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from . import __version__


LATEST_RELEASE_API = "https://api.github.com/repos/karimh97/Squeak/releases/latest"
LATEST_RELEASE_PAGE = "https://github.com/karimh97/Squeak/releases/latest"
_VERSION_PATTERN = re.compile(r"^[vV]?(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag_name: str
    title: str
    notes: str


def version_tuple(value: str) -> tuple[int, int, int]:
    """Return a comparable three-part version or raise for unsupported input."""
    match = _VERSION_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"Unsupported version: {value!r}")
    return tuple(int(part) for part in match.groups())


def is_newer_version(candidate: str, current: str = __version__) -> bool:
    return version_tuple(candidate) > version_tuple(current)


def parse_release_payload(payload: bytes) -> ReleaseInfo:
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("GitHub returned an unreadable update response.") from exc

    if not isinstance(data, dict) or data.get("draft") or data.get("prerelease"):
        raise ValueError("GitHub did not return a stable Squeak release.")

    tag_name = str(data.get("tag_name", "")).strip()
    version_tuple(tag_name)
    version = tag_name.lstrip("vV")
    title = str(data.get("name") or f"Squeak {tag_name}").strip()
    notes = str(data.get("body") or "").strip()
    return ReleaseInfo(version=version, tag_name=tag_name, title=title, notes=notes)


class UpdateChecker(QObject):
    """Fetch the latest stable release without blocking the application UI."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._network = QNetworkAccessManager(self)
        self._reply: QNetworkReply | None = None

    def check(self) -> bool:
        """Start a check, returning False when one is already in progress."""
        if self._reply is not None:
            return False

        request = QNetworkRequest(QUrl(LATEST_RELEASE_API))
        request.setTransferTimeout(10_000)
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"X-GitHub-Api-Version", b"2022-11-28")
        request.setRawHeader(b"User-Agent", f"Squeak/{__version__}".encode("ascii"))
        self._reply = self._network.get(request)
        self._reply.finished.connect(self._on_finished)
        return True

    def _on_finished(self) -> None:
        reply = self._reply
        self._reply = None
        if reply is None:
            return

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.failed.emit("Squeak could not reach GitHub to check for updates.")
                return
            try:
                release = parse_release_payload(bytes(reply.readAll()))
            except ValueError as exc:
                self.failed.emit(str(exc))
                return
            self.completed.emit(release)
        finally:
            reply.deleteLater()
