"""Core scoring engine: holds per-object timers, event log, pause/resume state."""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ObjectConfig:
    name: str
    hotkey: str


@dataclass
class ScoringEvent:
    object_name: str
    event_type: str  # 'start' or 'stop'
    t: float         # seconds from trial start (excluding paused time)


@dataclass
class ObjectStats:
    name: str
    total_time: float
    bouts: int
    mean_bout: float


class Scorer:
    """Toggle-style scorer: a hotkey press starts an exploration bout, the
    next press ends it. Trial time excludes any time the trial was paused."""

    def __init__(self, objects: list[ObjectConfig], duration: Optional[float] = None):
        self.objects = objects
        self.duration = duration  # seconds, or None for open-ended

        self.events: list[ScoringEvent] = []
        self._active_starts: dict[str, float] = {}        # object -> start t
        self._accum: dict[str, float] = {o.name: 0.0 for o in objects}
        self._bouts: dict[str, int] = {o.name: 0 for o in objects}

        self._t0: Optional[float] = None    # wall clock at trial start
        self._stopped: bool = False
        self._paused: bool = False
        self._pause_started_wall: Optional[float] = None
        self._paused_total: float = 0.0

    # --- lifecycle -----------------------------------------------------

    def start(self) -> None:
        if self._t0 is None:
            self._t0 = time.monotonic()

    def pause(self) -> None:
        if self._paused or self._stopped or self._t0 is None:
            return
        t = self.now()
        # Close any in-progress bouts at the moment of pause
        for name in list(self._active_starts.keys()):
            self._close_bout(name, t)
        self._paused = True
        self._pause_started_wall = time.monotonic()

    def resume(self) -> None:
        if not self._paused or self._stopped:
            return
        self._paused_total += time.monotonic() - (self._pause_started_wall or time.monotonic())
        self._paused = False
        self._pause_started_wall = None

    def stop(self) -> None:
        if self._stopped:
            return
        t = self.now()
        for name in list(self._active_starts.keys()):
            self._close_bout(name, t)
        self._stopped = True

    # --- scoring -------------------------------------------------------

    def toggle(self, object_name: str) -> bool:
        """Press the object's hotkey. Returns True if now actively scoring."""
        if self._t0 is None or self._paused or self._stopped:
            return object_name in self._active_starts
        if object_name not in self._accum:
            return False  # unknown object
        t = self.now()
        if object_name in self._active_starts:
            self._close_bout(object_name, t)
            return False
        self._active_starts[object_name] = t
        self._bouts[object_name] += 1
        self.events.append(ScoringEvent(object_name, 'start', t))
        return True

    def _close_bout(self, name: str, t: float) -> None:
        start = self._active_starts.pop(name, None)
        if start is None:
            return
        self._accum[name] += max(0.0, t - start)
        self.events.append(ScoringEvent(name, 'stop', t))

    # --- queries -------------------------------------------------------

    def now(self) -> float:
        if self._t0 is None:
            return 0.0
        if self._paused and self._pause_started_wall is not None:
            return self._pause_started_wall - self._t0 - self._paused_total
        return time.monotonic() - self._t0 - self._paused_total

    def time_for(self, name: str) -> float:
        base = self._accum.get(name, 0.0)
        if name in self._active_starts:
            base += max(0.0, self.now() - self._active_starts[name])
        return base

    def bouts_for(self, name: str) -> int:
        return self._bouts.get(name, 0)

    def is_active(self, name: str) -> bool:
        return name in self._active_starts

    def is_paused(self) -> bool:
        return self._paused

    def is_stopped(self) -> bool:
        return self._stopped

    def is_started(self) -> bool:
        return self._t0 is not None

    def is_complete(self) -> bool:
        if self.duration is None:
            return False
        return self.now() >= self.duration

    def stats(self) -> list[ObjectStats]:
        out = []
        for o in self.objects:
            n = o.name
            t = self.time_for(n)
            b = self.bouts_for(n)
            out.append(ObjectStats(n, t, b, (t / b) if b else 0.0))
        return out
