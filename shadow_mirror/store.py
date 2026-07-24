"""Local, self-owned persistence.

Everything lives in a single JSON file under the user's home directory by
default. No network, ever. The store also records an explicit consent
acknowledgement and supports full export and irreversible deletion, because
"the ability to refuse classification and to correct or delete the model" is a
structural requirement in your concept documents -- not a nice-to-have.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .engine import ShadowMirror
from .models import Observation

DEFAULT_PATH = Path.home() / ".shadow_mirror" / "journal.json"

CONSENT_TEXT = (
    "I am using the Shadow Mirror on myself, of my own accord. I understand its "
    "output is uncertain, dated, and not a statement of who I am; that it can be "
    "wrong; and that I can inspect, export, or delete all of it at any time."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = Path(path)

    # -- lifecycle ---------------------------------------------------------
    def exists(self) -> bool:
        return self.path.exists()

    def record_consent(self) -> None:
        data = self._read_raw()
        data["consent"] = {"text": CONSENT_TEXT, "acknowledged_at": _now_iso()}
        self._write_raw(data)

    def has_consent(self) -> bool:
        return bool(self._read_raw().get("consent"))

    # -- load / save -------------------------------------------------------
    def load(self) -> ShadowMirror:
        data = self._read_raw()
        mirror = ShadowMirror()
        rows = sorted(data.get("observations", []),
                      key=lambda r: r.get("timestamp", ""))
        for row in rows:
            obs = Observation.from_dict(row)  # preserves topic/reliability/timestamp
            mirror.observations.append(obs)
            # Replay the snapshot so reactivity/instability history rebuilds.
            mirror._update(obs.topic)
        return mirror

    def save(self, mirror: ShadowMirror) -> None:
        data = self._read_raw()
        data["observations"] = [o.to_dict() for o in mirror.observations]
        data["updated_at"] = _now_iso()
        self._write_raw(data)

    def export(self, dest: Path) -> Path:
        dest = Path(dest)
        dest.write_text(json.dumps(self._read_raw(), indent=2), encoding="utf-8")
        return dest

    def forget(self) -> None:
        """Irreversibly delete everything. The right to refuse, made real."""
        if self.path.exists():
            self.path.unlink()

    # -- raw io ------------------------------------------------------------
    def _read_raw(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "observations": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"version": 1, "observations": []}

    def _write_raw(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self.path)
