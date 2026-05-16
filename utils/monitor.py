import re
import time
import hashlib
from dataclasses import dataclass

LEVELS = ("ERROR", "WARNING", "CRITICAL")

TRACEBACK_START = "Traceback (most recent call last):"

@dataclass
class LogEvent:
    id: str
    level: str
    title: str
    exception_type: str | None
    traceback: str
    raw: str


def fingerprint(text: str):
    return hashlib.md5(text.encode()).hexdigest()


def monitor_log(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)

        buffer = []
        collecting = False

        while True:
            line = f.readline()

            if not line:
                time.sleep(0.1)
                continue

            line = line.rstrip()

            if any(level in line for level in LEVELS):
                if buffer:
                    yield parse_event(buffer)

                buffer = [line]
                collecting = True
                continue

            if collecting:
                buffer.append(line)

                if re.match(r"^\w*Error:", line) or re.match(r"^\w*Exception:", line):
                    yield parse_event(buffer)
                    buffer = []
                    collecting = False


def parse_event(lines):
    raw = "\n".join(lines)

    exc_match = re.search(r"(\w+(Error|Exception)):", raw)

    exc_type = exc_match.group(1) if exc_match else None

    title = exc_type or lines[0]

    return LogEvent(
        id=fingerprint(title),
        level=extract_level(lines[0]),
        title=title,
        exception_type=exc_type,
        traceback=raw,
        raw=raw,
    )


def extract_level(line):
    for level in LEVELS:
        if level in line:
            return level
    return "UNKNOWN"