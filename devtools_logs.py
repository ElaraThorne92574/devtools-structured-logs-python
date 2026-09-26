"""Ship and search events from a small developer-tools job."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from infrai import infrai


@dataclass(frozen=True)
class JobEvent:
    service: str
    level: str
    message: str
    timestamp: str
    attributes: dict[str, Any]


def event(service: str, level: str, message: str, **attributes: Any) -> JobEvent:
    return JobEvent(service, level, message, datetime.now(timezone.utc).isoformat(), attributes)


def ship_build(build_id: str, commit: str) -> dict:
    record = event("devtools-job", "info", "build completed", kind="build", build_id=build_id, commit=commit)
    return infrai.logs.ingest(entries=[asdict(record)])


def ship_release(release_id: str, environment: str) -> dict:
    record = event("devtools-job", "info", "release published", kind="release", release_id=release_id, environment=environment)
    return infrai.logs.ingest(entries=[asdict(record)])


def ship_diagnostic(check: str, passed: bool) -> dict:
    record = event("devtools-job", "info" if passed else "warn", "diagnostic finished", kind="diagnostic", check=check, passed=passed)
    return infrai.logs.ingest(entries=[asdict(record)])


def find_events(term: str) -> dict:
    return infrai.logs.search(q=term, service="devtools-job")


if __name__ == "__main__":
    print(ship_build("build-104", "a1b2c3d"))
    print(ship_release("release-22", "staging"))
    print(ship_diagnostic("dependency-lock", True))
    print(find_events("release"))
