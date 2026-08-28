#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = {
    "Unexplored",
    "Learning",
    "Needs Validation",
    "Mastered",
    "Needs Review",
}

MAP_LINK_RE = re.compile(r"^- \[\[([^|\]]+)\|([^\]]+)\]\]\s*$", re.MULTILINE)
PROGRESS_ROW_RE = re.compile(
    r"^\| \[\[([^|\]]+)\|([^\]]+)\]\] \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
    re.MULTILINE,
)


def _expect(expectations: list[dict[str, Any]], name: str, passed: bool, evidence: str) -> None:
    expectations.append({"text": name, "name": name, "passed": bool(passed), "evidence": evidence})


def _topic_workspace(vault: Path) -> Path | None:
    learn = vault / "Learn"
    if not learn.is_dir():
        return None
    topics = sorted(path for path in learn.iterdir() if path.is_dir())
    return topics[0] if len(topics) == 1 else None


def _parse_progress(text: str) -> list[dict[str, str]]:
    return [
        {
            "link": match.group(1),
            "title": match.group(2),
            "path": match.group(3).strip(),
            "status": match.group(4).strip(),
            "last_learned": match.group(5).strip(),
            "last_tested": match.group(6).strip(),
        }
        for match in PROGRESS_ROW_RE.finditer(text)
    ]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _final_assistant_text(events: Path | None) -> str:
    if events is None or not events.is_file():
        return ""
    final_text = ""
    for line in events.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "message_end":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant":
            continue
        content = message.get("content", [])
        if isinstance(content, str):
            final_text = content
            continue
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        if parts:
            final_text = "\n".join(parts)
    return final_text


def _verify_missing_mission(vault: Path, events: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    learn = vault / "Learn"
    written = list(learn.rglob("*")) if learn.exists() else []
    _expect(
        expectations,
        "missing mission writes no learning workspace",
        not learn.exists(),
        "Learn/ was not created" if not learn.exists() else f"Unexpected paths: {written}",
    )

    response = _final_assistant_text(events)
    normalized = response.lower()
    required_topics = {
        "why": ["why"],
        "current level": ["current level"],
        "target outcome": ["target", "outcome"],
        "success criteria": ["success", "should you be able", "able to do"],
        "constraints": ["constraint"],
        "out of scope": ["out of scope"],
    }
    missing_topics = [
        topic
        for topic, phrases in required_topics.items()
        if not any(phrase in normalized for phrase in phrases)
    ]
    _expect(
        expectations,
        "missing mission asks the required questions",
        not missing_topics,
        "All mission topics were requested"
        if not missing_topics
        else f"Missing question topics: {missing_topics}; response={response!r}",
    )
    return {
        "case": "missing-mission",
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_workspace(
    case: str,
    vault: Path,
    initial_vault: Path | None,
    research_unavailable: bool,
) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _topic_workspace(vault)

    _expect(
        expectations,
        "exactly one topic workspace exists",
        workspace is not None,
        str(workspace) if workspace else "Expected exactly one directory under Learn/",
    )
    if workspace is None:
        return {"case": case, "passed": False, "expectations": expectations}

    required_files = ["MISSION.md", "RESOURCES.md", "MAP.md", "PROGRESS.md", "HISTORY.md"]
    missing_files = [name for name in required_files if not (workspace / name).is_file()]
    _expect(
        expectations,
        "required state files exist",
        not missing_files,
        "All required files exist" if not missing_files else f"Missing: {missing_files}",
    )

    required_directories = ["lessons", "notes", "assessments"]
    missing_directories = [name for name in required_directories if not (workspace / name).is_dir()]
    _expect(
        expectations,
        "required artifact directories exist",
        not missing_directories,
        "All required directories exist"
        if not missing_directories
        else f"Missing: {missing_directories}",
    )

    root_entries = sorted(path.name for path in vault.iterdir())
    _expect(
        expectations,
        "writes stay inside Learn",
        root_entries == ["Learn"],
        f"Vault root entries: {root_entries}",
    )

    if missing_files:
        return {
            "case": case,
            "passed": all(item["passed"] for item in expectations),
            "expectations": expectations,
        }

    map_text = _read(workspace / "MAP.md")
    progress_text = _read(workspace / "PROGRESS.md")
    resources_text = _read(workspace / "RESOURCES.md")
    history_text = _read(workspace / "HISTORY.md")

    map_links = [match.group(1) for match in MAP_LINK_RE.finditer(map_text)]
    nested_links = re.findall(r"^[ \t]+- \[\[", map_text, re.MULTILINE)
    deep_headings = re.findall(r"^#{3,}\s", map_text, re.MULTILINE)
    _expect(
        expectations,
        "map has bounded two-level structure",
        0 < len(map_links) <= 25 and not nested_links and not deep_headings,
        f"concepts={len(map_links)}, nested_links={len(nested_links)}, deep_headings={len(deep_headings)}",
    )

    bad_map_paths = [path for path in map_links if not path.startswith("lessons/") or not path.endswith(".md")]
    _expect(
        expectations,
        "map links are path-qualified lessons",
        not bad_map_paths,
        "All map links target lessons/*.md" if not bad_map_paths else f"Invalid paths: {bad_map_paths}",
    )

    progress_rows = _parse_progress(progress_text)
    progress_paths = [row["path"] for row in progress_rows]
    duplicate_map = sorted({path for path in map_links if map_links.count(path) > 1})
    duplicate_progress = sorted({path for path in progress_paths if progress_paths.count(path) > 1})
    _expect(
        expectations,
        "map and progress paths match",
        set(map_links) == set(progress_paths) and not duplicate_map and not duplicate_progress,
        f"map={sorted(set(map_links))}, progress={sorted(set(progress_paths))}, "
        f"duplicate_map={duplicate_map}, duplicate_progress={duplicate_progress}",
    )

    invalid_statuses = [row for row in progress_rows if row["status"] not in ALLOWED_STATUSES]
    _expect(
        expectations,
        "progress statuses are valid",
        not invalid_statuses,
        "All statuses are valid" if not invalid_statuses else f"Invalid rows: {invalid_statuses}",
    )

    if case == "fresh-topic":
        invalid_initial = [
            row
            for row in progress_rows
            if row["status"] != "Unexplored"
            or row["last_learned"] != "—"
            or row["last_tested"] != "—"
        ]
        _expect(
            expectations,
            "fresh topics start unexplored with blank dates",
            not invalid_initial,
            "All rows are Unexplored with blank dates"
            if not invalid_initial
            else f"Invalid rows: {invalid_initial}",
        )
        current_focus_blank = bool(re.search(r"## Current Focus\s*\n\s*—\s*(?:\n|$)", progress_text))
        _expect(
            expectations,
            "fresh current focus is blank",
            current_focus_blank,
            "Current Focus is —" if current_focus_blank else "Current Focus was not —",
        )

    generated_learning_files = []
    for directory in ("lessons", "notes"):
        path = workspace / directory
        if path.exists():
            generated_learning_files.extend(item for item in path.rglob("*") if item.is_file())
    _expect(
        expectations,
        "learn creates no lesson or note files",
        not generated_learning_files,
        "lessons/ and notes/ contain no files"
        if not generated_learning_files
        else f"Unexpected files: {generated_learning_files}",
    )

    resource_headings = "## Knowledge" in resources_text and "## Further Reading" in resources_text
    _expect(
        expectations,
        "resources contain required headings",
        resource_headings,
        "Knowledge and Further Reading headings are present"
        if resource_headings
        else "Missing Knowledge or Further Reading heading",
    )
    if research_unavailable:
        resource_entries = re.findall(r"^- \[[^\]]+\]\([^)]+\)", resources_text, re.MULTILINE)
        _expect(
            expectations,
            "research-unavailable resources stay empty",
            not resource_entries,
            "No unverified resource entries were written"
            if not resource_entries
            else f"Unexpected entries: {resource_entries}",
        )
    _expect(
        expectations,
        "history records initialization",
        bool(history_text.strip()) and "# Learning History" in history_text,
        "Learning history initialized" if "# Learning History" in history_text else "History is empty or malformed",
    )

    if case == "partial-resume":
        initial_workspace = _topic_workspace(initial_vault) if initial_vault else None
        _expect(
            expectations,
            "resume fixture exists",
            initial_workspace is not None,
            str(initial_workspace) if initial_workspace else "Missing initial resume fixture",
        )
        if initial_workspace is not None:
            protected_files = ["MISSION.md", "MAP.md"]
            changed = [
                name
                for name in protected_files
                if (initial_workspace / name).is_file()
                and _read(initial_workspace / name) != _read(workspace / name)
            ]
            _expect(
                expectations,
                "resume preserves mission and map bytes",
                not changed,
                "MISSION.md and MAP.md preserved" if not changed else f"Changed: {changed}",
            )

            initial_progress = {
                row["path"]: row for row in _parse_progress(_read(initial_workspace / "PROGRESS.md"))
            }
            final_progress = {row["path"]: row for row in progress_rows}
            changed_rows = []
            for path, before in initial_progress.items():
                after = final_progress.get(path)
                if after is None or any(
                    before[field] != after[field]
                    for field in ("status", "last_learned", "last_tested")
                ):
                    changed_rows.append(path)
            _expect(
                expectations,
                "resume preserves existing progress state",
                not changed_rows,
                "Existing status and dates preserved"
                if not changed_rows
                else f"Changed rows: {changed_rows}",
            )

    return {
        "case": case,
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def verify_case(
    case: str,
    vault: Path,
    initial_vault: Path | None,
    events: Path | None,
    research_unavailable: bool = False,
) -> dict[str, Any]:
    if case == "missing-mission":
        return _verify_missing_mission(vault, events)
    if case not in {"fresh-topic", "partial-resume"}:
        raise ValueError(f"Unknown case: {case}")
    return _verify_workspace(case, vault, initial_vault, research_unavailable)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Learning OS /learn eval workspace")
    parser.add_argument("--case", required=True, choices=["fresh-topic", "partial-resume", "missing-mission"])
    parser.add_argument("--vault", type=Path, required=True)
    parser.add_argument("--initial-vault", type=Path)
    parser.add_argument("--events", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--research-unavailable", action="store_true")
    args = parser.parse_args()

    result = verify_case(
        args.case,
        args.vault,
        args.initial_vault,
        args.events,
        research_unavailable=args.research_unavailable,
    )
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
