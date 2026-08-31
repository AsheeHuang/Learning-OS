#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

NOTE_PATH = "notes/context-switch.md"
NOTE_LINK = "[[notes/context-switch.md|Context Switch]]"
SOURCE_PATH = "lessons/processes.md"
SOURCE_LINK = "[[lessons/processes.md|Processes]]"
ROW_RE = re.compile(
    r"^\| \[\[([^|]+)\|([^]]+)\]\] \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
    re.MULTILINE,
)


def expect(items: list[dict[str, Any]], name: str, passed: bool, evidence: str) -> None:
    items.append({"text": name, "name": name, "passed": bool(passed), "evidence": evidence})


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def snapshot(vault: Path) -> dict[str, bytes]:
    return {
        path.relative_to(vault).as_posix(): path.read_bytes()
        for path in sorted(vault.rglob("*"))
        if path.is_file()
    }


def workspaces(vault: Path) -> list[Path]:
    learn = vault / "Learn"
    return sorted(path for path in learn.iterdir() if path.is_dir()) if learn.is_dir() else []


def rows(text: str) -> list[dict[str, str]]:
    return [
        {
            "link": match.group(1),
            "title": match.group(2),
            "path": match.group(3).strip(),
            "status": match.group(4).strip(),
            "last_learned": match.group(5).strip(),
            "last_tested": match.group(6).strip(),
        }
        for match in ROW_RE.finditer(text)
    ]


def row_for(text: str, path: str) -> dict[str, str] | None:
    return next((row for row in rows(text) if row["path"] == path), None)


def current_focus(text: str) -> str:
    match = re.search(r"(?s)^## Current Focus\n\n(.*?)\n\n## Topics", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def assistant_text(events: Path | None) -> str:
    if events is None or not events.is_file():
        return ""
    messages: list[str] = []
    for line in events.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message", {})
        if event.get("type") == "message_end" and message.get("role") == "assistant":
            content = message.get("content", [])
            if isinstance(content, str):
                messages.append(content)
            else:
                messages.extend(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
    return "\n".join(messages)


def verify_ambiguity(vault: Path, initial_vault: Path | None, events: Path | None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    unchanged = bool(initial_vault and snapshot(vault) == snapshot(initial_vault))
    response = assistant_text(events)
    choose = bool(re.search(r"choose|select|which|ambiguous|workspace|source", response, re.IGNORECASE))
    expect(checks, "ambiguous source creates no artifact", unchanged, "Vault snapshot preserved" if unchanged else "Vault changed")
    expect(checks, "ambiguous source asks for disambiguation", choose, response)
    return {"case": "note-ambiguity", "passed": all(item["passed"] for item in checks), "expectations": checks}


def verify_complete(case: str, vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    topics = workspaces(vault)
    expect(checks, "one topic workspace exists", len(topics) == 1, f"workspaces={[path.name for path in topics]}")
    if len(topics) != 1 or initial_vault is None:
        return {"case": case, "passed": False, "expectations": checks}

    root = topics[0]
    initial_topics = workspaces(initial_vault)
    initial_root = initial_topics[0] if len(initial_topics) == 1 else None
    if initial_root is None:
        expect(checks, "initial fixture has one topic workspace", False, f"workspaces={[path.name for path in initial_topics]}")
        return {"case": case, "passed": False, "expectations": checks}

    note = root / NOTE_PATH
    source = root / SOURCE_PATH
    progress = root / "PROGRESS.md"
    history = root / "HISTORY.md"
    map_file = root / "MAP.md"
    required = [note, source, progress, history, map_file]
    expect(checks, "note and state files exist", all(path.is_file() for path in required), str([path.name for path in required]))
    if not all(path.is_file() for path in required):
        return {"case": case, "passed": False, "expectations": checks}

    note_text = read(note)
    source_text = read(source)
    progress_text = read(progress)
    initial_progress_text = read(initial_root / "PROGRESS.md")
    initial_source_text = read(initial_root / SOURCE_PATH)
    initial_map_text = read(initial_root / "MAP.md")
    initial_history_text = read(initial_root / "HISTORY.md")
    history_text = read(history)

    headings = all(f"## {heading}" in note_text for heading in (
        "Question", "Explanation", "Connection to the Source", "Related Concepts", "Sources"
    ))
    expect(checks, "note has the protocol sections", headings, note_text)
    expect(checks, "note links to the source", NOTE_LINK not in note_text and SOURCE_LINK in note_text, note_text)
    expect(checks, "source links back exactly once", source_text.count(NOTE_LINK) == 1, f"count={source_text.count(NOTE_LINK)}")

    final_row = row_for(progress_text, NOTE_PATH)
    initial_row = row_for(initial_progress_text, NOTE_PATH)
    expect(checks, "note progress row is Learning with today's date", bool(final_row and final_row["status"] == "Learning" and final_row["last_learned"] == date.today().isoformat()), str(final_row))
    if initial_row:
        expect(checks, "existing Last Tested is preserved", final_row and final_row["last_tested"] == initial_row["last_tested"], f"initial={initial_row}, final={final_row}")
    else:
        expect(checks, "new note starts with no Last Tested date", bool(final_row and final_row["last_tested"] == "—"), str(final_row))

    expect(checks, "source status and protected focus are preserved", current_focus(progress_text) == current_focus(initial_progress_text), f"initial={current_focus(initial_progress_text)}, final={current_focus(progress_text)}")
    source_before = row_for(initial_progress_text, SOURCE_PATH)
    source_after = row_for(progress_text, SOURCE_PATH)
    expect(checks, "source row is unchanged", source_before == source_after, f"initial={source_before}, final={source_after}")

    if case == "note-promotion":
        map_text = read(map_file)
        expect(checks, "explicit promotion adds one note map link", map_text.count(NOTE_LINK) == 1 and map_text != initial_map_text, f"count={map_text.count(NOTE_LINK)}")
    else:
        expect(checks, "side exploration leaves map unchanged", read(map_file) == initial_map_text, "MAP.md preserved")

    event_count = len(re.findall(r"^### Explored: Context Switch\s*$", history_text, re.MULTILINE))
    initial_event_count = len(re.findall(r"^### Explored: Context Switch\s*$", initial_history_text, re.MULTILINE))
    expect(checks, "history remains append-only", history_text.startswith(initial_history_text), "Existing history is preserved" if history_text.startswith(initial_history_text) else "History was rewritten")
    expect(checks, "history has one exploration event", event_count == max(1, initial_event_count), f"initial={initial_event_count}, final={event_count}")

    if case == "note-resume":
        expect(checks, "partial note preserves human content", "Human note: preserve this observation." in note_text, note_text)
    if case == "note-unverified":
        expect(checks, "unverified fallback is explicit", "unverified" in note_text.lower(), note_text)
        expect(checks, "unverified fallback invents no URL", not re.search(r"https?://", note_text), note_text)

    return {"case": case, "passed": all(item["passed"] for item in checks), "expectations": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=["note-create", "note-resume", "note-promotion", "note-unverified", "note-ambiguity"])
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--initial-vault", type=Path)
    parser.add_argument("--events", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.case == "note-ambiguity":
        result = verify_ambiguity(args.vault, args.initial_vault, args.events)
    else:
        result = verify_complete(args.case, args.vault, args.initial_vault)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    label = "PASS" if result["passed"] else "FAIL"
    print(f"{label} {args.case}")
    for item in result["expectations"]:
        mark = "PASS" if item["passed"] else "FAIL"
        print(f"  {mark} {item['name']}: {item['evidence']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
