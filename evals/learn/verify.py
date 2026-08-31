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


def _vault_snapshot(vault: Path, exclude_assessments: bool = False) -> dict[str, bytes]:
    snapshot: dict[str, bytes] = {}
    for path in sorted(item for item in vault.rglob("*") if item.is_file()):
        relative = path.relative_to(vault).as_posix()
        if exclude_assessments and "/assessments/" in f"/{relative}":
            continue
        snapshot[relative] = path.read_bytes()
    return snapshot


def _assessment_topic_links(text: str) -> list[str]:
    match = re.search(r"^- Topics:\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    return re.findall(r"^\s+- \[\[([^]]+)\]\]\s*$", match.group(1), re.MULTILINE)


def _question_blocks(section: str) -> list[dict[str, str]]:
    labels = {
        "Source section",
        "Prompt",
        "Learner answer",
        "Clarification prompt",
        "Clarified answer",
        "Feedback",
        "Diagnosis",
        "Remediation prompt",
        "Revised answer",
        "Follow-up feedback",
        "Dispute",
        "Resolution",
        "Revision note",
        "Evidence",
        "Expected key points",
        "Result",
    }
    blocks: list[dict[str, str]] = []
    for match in re.finditer(
        r"^### .*?\bQuestion\b[^\n]*\n(.*?)(?=^### .*?\bQuestion\b|^### Topic Outcome|\Z)",
        section,
        re.MULTILINE | re.DOTALL,
    ):
        fields: dict[str, list[str]] = {}
        current: str | None = None
        for line in match.group(1).splitlines():
            field_match = re.match(r"^([A-Za-z -]+):\s*(.*)$", line)
            if field_match and field_match.group(1) in labels:
                current = field_match.group(1)
                fields.setdefault(current, [])
                if field_match.group(2).strip():
                    fields[current].append(field_match.group(2).strip())
            elif current is not None and line.strip():
                fields[current].append(line.strip())
        blocks.append({key: "\n".join(value).strip() for key, value in fields.items()})
    return blocks


def _assistant_messages(events: Path | None) -> list[str]:
    if events is None or not events.is_file():
        return []
    messages: list[str] = []
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
            messages.append(content)
            continue
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        if parts:
            messages.append("\n".join(parts))
    return messages


def _assistant_transcript(events: Path | None) -> str:
    return "\n".join(_assistant_messages(events))


def _final_assistant_text(events: Path | None) -> str:
    messages = _assistant_messages(events)
    return messages[-1] if messages else ""


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


QUIZ_CASES = {
    "quiz-strong": {
        "topic": "Processes",
        "path": "lessons/processes.md",
        "outcome": "strong",
        "grounding": "verified",
        "status": "Mastered",
        "require_source_sections": True,
    },
    "quiz-remediation": {
        "topic": "Threads",
        "path": "lessons/threads.md",
        "outcome": "partial",
        "grounding": "verified",
        "status": "Needs Review",
        "diagnosis": "concept-confusion",
        "remediation": True,
    },
    "quiz-unknown": {
        "topic": "Threads",
        "path": "lessons/threads.md",
        "outcome": "weak",
        "grounding": "verified",
        "status": "Needs Review",
        "diagnosis": "knowledge-gap",
        "remediation": True,
    },
    "quiz-unverified": {
        "topic": "Context Switch",
        "path": "notes/context-switch.md",
        "outcome": "partial",
        "grounding": "unverified",
        "status": "Needs Review",
    },
    "quiz-finalization": {
        "topic": "Processes",
        "path": "lessons/processes.md",
        "outcome": "strong",
        "grounding": "verified",
        "status": "Mastered",
    },
}


def _assessment_files(workspace: Path) -> list[Path]:
    assessments = workspace / "assessments"
    return sorted(assessments.glob("*.md")) if assessments.is_dir() else []


def _assessment_status(text: str) -> str | None:
    match = re.search(r"^- Status: (in-progress|complete|abandoned)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def _topic_section(text: str, topic: str) -> str:
    match = re.search(
        rf"^## Topic: {re.escape(topic)}\s*$\n(.*?)(?=^## Topic: |^## Misconceptions\s*$|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _current_focus(text: str) -> str:
    match = re.search(r"^## Current Focus\s*$\n\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1) if match else ""


def _workspace_by_name(vault: Path, name: str = "Operating Systems") -> Path | None:
    workspace = vault / "Learn" / name
    return workspace if workspace.is_dir() else None


def _compare_quiz_progress(
    expectations: list[dict[str, Any]],
    initial_workspace: Path,
    workspace: Path,
    target_path: str,
    expected_status: str,
    expected_tested_date: str,
    preserve_applied_target: bool = False,
) -> None:
    before_text = _read(initial_workspace / "PROGRESS.md")
    after_text = _read(workspace / "PROGRESS.md")
    before = {row["path"]: row for row in _parse_progress(before_text)}
    after = {row["path"]: row for row in _parse_progress(after_text)}
    target_before = before.get(target_path)
    target_after = after.get(target_path)

    target_valid = bool(
        target_before
        and target_after
        and target_after["status"] == expected_status
        and target_after["last_learned"] == target_before["last_learned"]
        and target_after["last_tested"] == expected_tested_date
        and (not preserve_applied_target or target_after == target_before)
    )
    _expect(
        expectations,
        "tested topic has the expected status and dates",
        target_valid,
        f"before={target_before}, after={target_after}",
    )

    changed_unrelated = [
        path
        for path, row in before.items()
        if path != target_path and after.get(path) != row
    ]
    _expect(
        expectations,
        "unselected progress rows are preserved",
        not changed_unrelated,
        "All unselected rows preserved" if not changed_unrelated else f"Changed: {changed_unrelated}",
    )
    focus_preserved = _current_focus(before_text) == _current_focus(after_text)
    _expect(
        expectations,
        "current focus is preserved",
        focus_preserved,
        f"before={_current_focus(before_text)!r}, after={_current_focus(after_text)!r}",
    )


def _verify_complete_quiz(
    case: str,
    vault: Path,
    initial_vault: Path | None,
    events: Path | None,
) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    config = QUIZ_CASES[case]
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None

    _expect(
        expectations,
        "quiz workspace exists",
        workspace is not None,
        str(workspace) if workspace else "Missing Learn/Operating Systems",
    )
    if workspace is None or initial_workspace is None:
        _expect(expectations, "initial quiz fixture exists", False, "Initial workspace is required")
        return {"case": case, "passed": False, "expectations": expectations}

    complete = []
    for path in _assessment_files(workspace):
        text = _read(path)
        if _assessment_status(text) == "complete" and f"|{config['topic']}]]" in text:
            complete.append(path)
    _expect(
        expectations,
        "exactly one matching complete assessment exists",
        len(complete) == 1,
        f"matching={[path.name for path in complete]}",
    )
    if len(complete) != 1:
        return {"case": case, "passed": False, "expectations": expectations}

    assessment = complete[0]
    text = _read(assessment)
    section = _topic_section(text, config["topic"])
    _expect(
        expectations,
        "assessment groups evidence under the selected topic",
        bool(section),
        f"topic={config['topic']}",
    )

    initial_rows = {
        row["path"]: row for row in _parse_progress(_read(initial_workspace / "PROGRESS.md"))
    }
    baseline = {
        "path": (re.search(r"^- Path:\s*(\S+)\s*$", section, re.MULTILINE) or [None, ""])[1],
        "status": (re.search(r"^- Starting status:\s*(.+?)\s*$", section, re.MULTILINE) or [None, ""])[1],
        "last_learned": (re.search(r"^- Starting Last Learned:\s*(.+?)\s*$", section, re.MULTILINE) or [None, ""])[1],
        "last_tested": (re.search(r"^- Starting Last Tested:\s*(.+?)\s*$", section, re.MULTILINE) or [None, ""])[1],
    }
    initial_target = initial_rows.get(config["path"])
    baseline_valid = bool(
        baseline["path"] == config["path"]
        and baseline["status"] in {"Needs Validation", "Needs Review"}
        and baseline["last_learned"]
        and baseline["last_tested"]
        and (
            case == "quiz-finalization"
            or not initial_target
            or all(
                baseline[field] == initial_target[field]
                for field in ("status", "last_learned", "last_tested")
            )
        )
    )
    _expect(
        expectations,
        "assessment persists the selected row baseline",
        baseline_valid,
        f"baseline={baseline}, initial={initial_target}",
    )

    questions = _question_blocks(section)
    required_fields = ["Prompt", "Learner answer", "Feedback", "Evidence", "Expected key points", "Result"]
    invalid_questions = [
        index
        for index, question in enumerate(questions, 1)
        if any(not question.get(field, "").strip() for field in required_fields)
        or question.get("Result", "").splitlines()[-1].strip() not in {"strong", "partial", "weak"}
    ]
    minimum_prompts = 1 if config["outcome"] == "weak" else 2
    if config.get("require_source_sections"):
        lesson_text = _read(workspace / config["path"])
        invalid_source_sections = [
            index
            for index, question in enumerate(questions, 1)
            if not question.get("Source section", "").strip()
            or not re.search(
                rf"^{re.escape(question['Source section'].strip())}\s*$",
                lesson_text,
                re.MULTILINE,
            )
        ]
        _expect(
            expectations,
            "questions cite existing lesson headings",
            not invalid_source_sections,
            f"invalid_source_sections={invalid_source_sections}",
        )
    _expect(
        expectations,
        "each question contains non-empty durable evidence fields",
        len(questions) >= minimum_prompts and not invalid_questions,
        f"questions={len(questions)}, invalid={invalid_questions}",
    )
    if events is not None and questions:
        transcript = _assistant_transcript(events)
        visible_feedback = (
            len(re.findall(r"(?im)^\s*(?:Feedback|回饋)\s*[:：]", transcript)) >= len(questions)
            and len(
                re.findall(
                    r"(?im)^\s*(?:Correct answer(?:/core model)?|正確答案|核心模型)\s*[:：]",
                    transcript,
                )
            )
            >= len(questions)
        )
        _expect(
            expectations,
            "feedback and correct answer are visible in chat",
            visible_feedback,
            "Visible feedback markers found" if visible_feedback else "Feedback only appears in the assessment or is missing",
        )

    outcome_pattern = re.compile(
        rf"^### Topic Outcome\s*$.*?^Grounding: {re.escape(config['grounding'])}\s*$.*?^Result: {re.escape(config['outcome'])}\s*$.*?^Evidence summary:\s*\S",
        re.MULTILINE | re.DOTALL,
    )
    _expect(
        expectations,
        "topic outcome and grounding match the case",
        bool(outcome_pattern.search(section)),
        f"expected grounding={config['grounding']}, result={config['outcome']}",
    )

    diagnosis = config.get("diagnosis")
    if diagnosis:
        matching_diagnoses = [
            question.get("Diagnosis", "")
            for question in questions
            if question.get("Diagnosis", "").startswith(diagnosis)
        ]
        _expect(
            expectations,
            "diagnosis identifies the expected gap",
            bool(matching_diagnoses),
            f"expected diagnosis={diagnosis}, actual={[question.get('Diagnosis') for question in questions]}",
        )
    if config.get("remediation"):
        remediated = [
            question
            for question in questions
            if all(
                question.get(field, "").strip()
                for field in ("Remediation prompt", "Revised answer", "Follow-up feedback")
            )
        ]
        _expect(
            expectations,
            "remediation preserves non-empty original and revised turns",
            len(remediated) == 1,
            f"remediated_questions={len(remediated)}",
        )

    has_session_sections = all(
        heading in text for heading in ("## Misconceptions", "## Summary", "## Progress Changes")
    )
    _expect(
        expectations,
        "completed assessment contains session summary sections",
        has_session_sections,
        "All session sections present" if has_session_sections else "Missing a session summary section",
    )

    date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.MULTILINE)
    assessment_date = date_match.group(1) if date_match else ""
    _expect(
        expectations,
        "assessment has an ISO date",
        bool(assessment_date),
        f"date={assessment_date!r}",
    )
    _compare_quiz_progress(
        expectations,
        initial_workspace,
        workspace,
        config["path"],
        config["status"],
        assessment_date,
        preserve_applied_target=case == "quiz-finalization",
    )

    initial_history = _read(initial_workspace / "HISTORY.md")
    final_history = _read(workspace / "HISTORY.md")
    assessment_ref = f"[[assessments/{assessment.name}|"
    appended_history = final_history[len(initial_history):] if final_history.startswith(initial_history) else ""
    history_valid = bool(
        final_history.startswith(initial_history)
        and final_history.count(assessment_ref) == 1
        and config["topic"] in appended_history
        and re.search(rf"^- Outcome:\s*`?{re.escape(config['outcome'])}`?\s*$", appended_history, re.MULTILINE)
        and re.search(
            rf"^- Status:\s*`?{re.escape(baseline['status'])}`?\s*→\s*`?{re.escape(config['status'])}`?\s*$",
            appended_history,
            re.MULTILINE,
        )
    )
    _expect(
        expectations,
        "history appends one event with outcome and transition",
        history_valid,
        f"link_count={final_history.count(assessment_ref)}, appended={appended_history!r}",
    )

    if events is not None and case not in {"quiz-resume", "quiz-finalization"}:
        first_snapshot = events.parent / "snapshots" / "turn-1-vault" / "Learn" / "Operating Systems" / "assessments" / assessment.name
        if first_snapshot.is_file():
            first_text = _read(first_snapshot)
            first_questions = _question_blocks(_topic_section(first_text, config["topic"]))
            persisted_before_answer = bool(
                _assessment_status(first_text) == "in-progress"
                and first_questions
                and first_questions[0].get("Prompt")
                and not first_questions[0].get("Learner answer")
            )
            _expect(
                expectations,
                "first prompt is durable before the learner answer",
                persisted_before_answer,
                f"first_question={first_questions[0] if first_questions else None}",
            )

    return {
        "case": case,
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_quiz_in_progress(vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz interruption fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-in-progress", "passed": False, "expectations": expectations}

    in_progress = [
        path for path in _assessment_files(workspace) if _assessment_status(_read(path)) == "in-progress"
    ]
    _expect(
        expectations,
        "one in-progress assessment remains resumable",
        len(in_progress) == 1,
        f"in_progress={[path.name for path in in_progress]}",
    )
    progress_same = _read(workspace / "PROGRESS.md") == _read(initial_workspace / "PROGRESS.md")
    history_same = _read(workspace / "HISTORY.md") == _read(initial_workspace / "HISTORY.md")
    _expect(
        expectations,
        "in-progress assessment leaves progress unchanged",
        progress_same,
        "PROGRESS.md preserved" if progress_same else "PROGRESS.md changed before completion",
    )
    _expect(
        expectations,
        "in-progress assessment leaves history unchanged",
        history_same,
        "HISTORY.md preserved" if history_same else "HISTORY.md changed before completion",
    )
    if len(in_progress) == 1:
        text = _read(in_progress[0])
        _expect(
            expectations,
            "in-progress artifact retains an unanswered prompt",
            "Prompt:" in text,
            "Persisted prompt found" if "Prompt:" in text else "No persisted prompt",
        )
        initial_assessment = initial_workspace / "assessments" / in_progress[0].name
        if initial_assessment.is_file():
            preserved = text.startswith(_read(initial_assessment))
            _expect(
                expectations,
                "interruption preserves the prior assessment prefix",
                preserved,
                "Prior artifact preserved" if preserved else "Prior artifact was regenerated",
            )
    return {
        "case": "quiz-in-progress",
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_quiz_resume(vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz resume fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-resume", "passed": False, "expectations": expectations}

    initial_files = _assessment_files(initial_workspace)
    final_files = _assessment_files(workspace)
    same_file_set = [path.name for path in initial_files] == [path.name for path in final_files]
    _expect(
        expectations,
        "resume reuses the existing assessment artifact",
        len(final_files) == 1 and same_file_set,
        f"initial={[path.name for path in initial_files]}, final={[path.name for path in final_files]}",
    )
    if len(initial_files) != 1 or len(final_files) != 1:
        return {"case": "quiz-resume", "passed": False, "expectations": expectations}

    initial_text = _read(initial_files[0])
    final_text = _read(final_files[0])
    lifecycle_valid = _assessment_status(initial_text) == "in-progress" and _assessment_status(final_text) == "complete"
    normalized_final = final_text.replace("- Status: complete", "- Status: in-progress", 1)
    preserved = normalized_final.startswith(initial_text)
    pending_prompt = "Two threads update one shared queue without synchronization. Predict a failure and explain why separate stacks do not prevent it."
    prompt_reused = final_text.count(pending_prompt) == 1
    _expect(expectations, "resume completes the prior lifecycle", lifecycle_valid, f"initial={_assessment_status(initial_text)}, final={_assessment_status(final_text)}")
    _expect(expectations, "resume appends to the durable prior artifact", preserved, "Initial artifact is a preserved prefix" if preserved else "Initial artifact was regenerated")
    _expect(expectations, "resume reuses the exact unanswered prompt", prompt_reused, f"prompt_count={final_text.count(pending_prompt)}")

    topic_outcomes = all(
        re.search(r"^### Topic Outcome\s*$.*?^Result: strong\s*$", _topic_section(final_text, topic), re.MULTILINE | re.DOTALL)
        for topic in ("Processes", "Threads")
    )
    _expect(expectations, "both resumed topics have strong outcomes", bool(topic_outcomes), "Processes and Threads outcomes checked")

    before_text = _read(initial_workspace / "PROGRESS.md")
    after_text = _read(workspace / "PROGRESS.md")
    before = {row["path"]: row for row in _parse_progress(before_text)}
    after = {row["path"]: row for row in _parse_progress(after_text)}
    selected = {"lessons/processes.md", "lessons/threads.md"}
    date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})\s*$", final_text, re.MULTILINE)
    assessment_date = date_match.group(1) if date_match else ""
    topic_names = {"lessons/processes.md": "Processes", "lessons/threads.md": "Threads"}
    baselines_valid = all(
        re.search(rf"^- Path:\s*{re.escape(path)}\s*$", _topic_section(final_text, topic_names[path]), re.MULTILINE)
        and re.search(rf"^- Starting status:\s*{re.escape(before[path]['status'])}\s*$", _topic_section(final_text, topic_names[path]), re.MULTILINE)
        and re.search(rf"^- Starting Last Learned:\s*{re.escape(before[path]['last_learned'])}\s*$", _topic_section(final_text, topic_names[path]), re.MULTILINE)
        and re.search(rf"^- Starting Last Tested:\s*{re.escape(before[path]['last_tested'])}\s*$", _topic_section(final_text, topic_names[path]), re.MULTILINE)
        for path in selected
    )
    _expect(expectations, "resumed topics retain their durable baselines", bool(baselines_valid), f"date={assessment_date}")
    selected_valid = all(
        after.get(path)
        and after[path]["status"] == "Mastered"
        and after[path]["last_learned"] == before[path]["last_learned"]
        and after[path]["last_tested"] == assessment_date
        for path in selected
    )
    unrelated_valid = all(after.get(path) == row for path, row in before.items() if path not in selected)
    focus_valid = _current_focus(before_text) == _current_focus(after_text)
    _expect(expectations, "resumed topics finalize atomically", selected_valid, f"selected_after={{path: after.get(path) for path in selected}}")
    _expect(expectations, "resume preserves unselected progress and current focus", unrelated_valid and focus_valid, f"unrelated={unrelated_valid}, focus={focus_valid}")

    initial_history = _read(initial_workspace / "HISTORY.md")
    final_history = _read(workspace / "HISTORY.md")
    assessment_ref = f"[[assessments/{final_files[0].name}|"
    appended_history = final_history[len(initial_history):] if final_history.startswith(initial_history) else ""
    outcome_lines = re.findall(r"^- .*?Outcome:.*$", appended_history, re.MULTILINE)
    status_lines = re.findall(r"^- .*?Status:.*$", appended_history, re.MULTILINE)
    topic_outcomes_valid = all(
        any(
            re.search(rf"\b{re.escape(topic)}\b", line, re.IGNORECASE)
            and re.search(r"\bstrong\b", line, re.IGNORECASE)
            for line in outcome_lines
        )
        for topic in ("Processes", "Threads")
    )
    topic_statuses_valid = all(
        any(
            re.search(rf"\b{re.escape(topic)}\b", line, re.IGNORECASE)
            and re.search(r"Needs Validation\s*`?\s*→\s*`?\s*Mastered", line, re.IGNORECASE)
            for line in status_lines
        )
        for topic in ("Processes", "Threads")
    )
    separate_topic_history = bool(
        topic_outcomes_valid
        and topic_statuses_valid
    ) or all(
        re.search(
            rf"^- Topic:.*\b{re.escape(topic)}\b.*\n"
            r"^- Outcome:\s*`?strong`?\s*$.*\n"
            r"^- Status:\s*`?Needs Validation`?\s*→\s*`?Mastered`?\s*$",
            appended_history,
            re.MULTILINE,
        )
        for topic in ("Processes", "Threads")
    )
    history_valid = bool(
        final_history.startswith(initial_history)
        and final_history.count(assessment_ref) == 1
        and all(topic in appended_history for topic in ("Processes", "Threads"))
        and separate_topic_history
    )
    _expect(expectations, "resume appends one linked history event with both outcomes", history_valid, f"link_count={final_history.count(assessment_ref)}, appended={appended_history!r}")
    return {
        "case": "quiz-resume",
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_quiz_abandon(vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz abandon fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-abandon", "passed": False, "expectations": expectations}
    by_status: dict[str, list[Path]] = {"abandoned": [], "in-progress": [], "complete": []}
    for path in _assessment_files(workspace):
        status = _assessment_status(_read(path))
        if status in by_status:
            by_status[status].append(path)
    _expect(
        expectations,
        "abandoned attempt and distinct fresh attempt are preserved",
        len(by_status["abandoned"]) == 1 and len(by_status["in-progress"]) == 1,
        str({key: [path.name for path in value] for key, value in by_status.items()}),
    )
    abandoned_text = _read(by_status["abandoned"][0]) if len(by_status["abandoned"]) == 1 else ""
    fresh_text = _read(by_status["in-progress"][0]) if len(by_status["in-progress"]) == 1 else ""
    expected_topics = ["lessons/processes.md|Processes", "lessons/threads.md|Threads"]
    abandoned_questions = _question_blocks(_topic_section(abandoned_text, "Processes"))
    fixed_topics = (
        _assessment_topic_links(abandoned_text) == expected_topics
        and _assessment_topic_links(fresh_text) == expected_topics
    )
    preserved_turn = bool(
        abandoned_questions
        and abandoned_questions[0].get("Prompt")
        and abandoned_questions[0].get("Learner answer")
    )
    _expect(
        expectations,
        "abandoned attempt preserves its fixed topic set and recorded turn",
        fixed_topics and preserved_turn,
        f"abandoned_topics={_assessment_topic_links(abandoned_text)}, fresh_topics={_assessment_topic_links(fresh_text)}, turn={abandoned_questions[:1]}",
    )
    distinct = bool(
        by_status["abandoned"]
        and by_status["in-progress"]
        and by_status["abandoned"][0].name != by_status["in-progress"][0].name
        and re.search(r"-\d+\.md$", by_status["in-progress"][0].name)
    )
    _expect(
        expectations,
        "fresh attempt uses a numeric suffix",
        distinct,
        "Distinct suffixed file found" if distinct else "Fresh attempt did not use a suffix",
    )
    protected_same = _vault_snapshot(vault, exclude_assessments=True) == _vault_snapshot(
        initial_vault, exclude_assessments=True
    )
    _expect(
        expectations,
        "abandonment changes only assessment artifacts",
        protected_same,
        "Non-assessment vault snapshot preserved" if protected_same else "A non-assessment file changed",
    )
    return {
        "case": "quiz-abandon",
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_quiz_candidates(vault: Path, initial_vault: Path | None, events: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz candidate fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-candidates", "passed": False, "expectations": expectations}
    no_assessment = not _assessment_files(workspace)
    protected = _vault_snapshot(vault) == _vault_snapshot(initial_vault)
    response = _final_assistant_text(events)
    candidates_present = all(topic in response for topic in ("Processes", "Threads", "Context Switch"))
    unexplored_excluded = "Scheduling" not in response
    asks_confirmation = bool(re.search(r"confirm|choose|select|exclude|which", response, re.IGNORECASE))
    _expect(expectations, "candidate selection creates no assessment", no_assessment, f"assessments={[path.name for path in _assessment_files(workspace)]}")
    _expect(expectations, "candidate selection preserves the complete vault", protected, "Vault snapshot preserved" if protected else "The vault changed before confirmation")
    _expect(expectations, "response lists only eligible candidates", candidates_present and unexplored_excluded, response)
    _expect(expectations, "response asks the learner to confirm the set", asks_confirmation, response)
    return {
        "case": "quiz-candidates",
        "passed": all(item["passed"] for item in expectations),
        "expectations": expectations,
    }


def _verify_quiz_interruption(
    vault: Path,
    initial_vault: Path | None,
    events: Path | None,
) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz interruption fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-interruption", "passed": False, "expectations": expectations}
    in_progress = [path for path in _assessment_files(workspace) if _assessment_status(_read(path)) == "in-progress"]
    _expect(expectations, "interruption leaves one in-progress assessment", len(in_progress) == 1, f"files={[path.name for path in in_progress]}")
    if len(in_progress) != 1:
        return {"case": "quiz-interruption", "passed": False, "expectations": expectations}
    text = _read(in_progress[0])
    processes = _topic_section(text, "Processes")
    threads = _topic_section(text, "Threads")
    process_questions = _question_blocks(processes)
    thread_questions = _question_blocks(threads)
    process_complete = bool(
        len(process_questions) >= 2
        and all(
            all(question.get(field) for field in ("Prompt", "Learner answer", "Feedback", "Evidence", "Expected key points", "Result"))
            for question in process_questions
        )
        and re.search(r"^### Topic Outcome\s*$.*?^Result:\s*(strong|partial|weak)\s*$", processes, re.MULTILINE | re.DOTALL)
    )
    thread_pending = bool(
        thread_questions
        and thread_questions[0].get("Prompt")
        and not thread_questions[0].get("Learner answer")
    )
    _expect(expectations, "completed first-topic evidence is durable", process_complete, f"questions={process_questions}")
    _expect(expectations, "next topic has one durable unanswered prompt", thread_pending, f"questions={thread_questions}")
    protected = _vault_snapshot(vault, exclude_assessments=True) == _vault_snapshot(initial_vault, exclude_assessments=True)
    _expect(expectations, "interrupted batch preserves every non-assessment file", protected, "Non-assessment snapshot preserved" if protected else "A protected file changed")
    if events is not None:
        snapshots = events.parent / "snapshots"
        first_files = list((snapshots / "turn-1-vault" / "Learn" / "Operating Systems" / "assessments").glob("*.md"))
        first_ordered = False
        if len(first_files) == 1:
            first_questions = _question_blocks(_topic_section(_read(first_files[0]), "Processes"))
            first_ordered = bool(first_questions and first_questions[0].get("Prompt") and not first_questions[0].get("Learner answer"))
        _expect(expectations, "first prompt is snapshotted before its answer", first_ordered, f"snapshot_files={[path.name for path in first_files]}")
    return {"case": "quiz-interruption", "passed": all(item["passed"] for item in expectations), "expectations": expectations}


def _verify_quiz_dispute(vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    workspace = _workspace_by_name(vault)
    initial_workspace = _workspace_by_name(initial_vault) if initial_vault else None
    if workspace is None or initial_workspace is None:
        _expect(expectations, "quiz dispute fixtures exist", False, "Missing initial or final workspace")
        return {"case": "quiz-dispute", "passed": False, "expectations": expectations}
    in_progress = [path for path in _assessment_files(workspace) if _assessment_status(_read(path)) == "in-progress"]
    _expect(expectations, "unresolved dispute remains in progress", len(in_progress) == 1, f"files={[path.name for path in in_progress]}")
    text = _read(in_progress[0]) if len(in_progress) == 1 else ""
    questions = _question_blocks(_topic_section(text, "Context Switch"))
    dispute_recorded = any(question.get("Dispute") and question.get("Resolution") for question in questions)
    unresolved = any(re.search(r"unresolved|cannot|not .*settle|insufficient", question.get("Resolution", ""), re.IGNORECASE) for question in questions)
    unfinished = "### Topic Outcome" not in text and "## Progress Changes" not in text
    _expect(expectations, "dispute and unresolved resolution are durable", dispute_recorded and unresolved, f"questions={questions}")
    _expect(expectations, "unresolved dispute has no final outcome", unfinished, "No outcome or progress changes" if unfinished else "Assessment was prematurely finalized")
    protected = _vault_snapshot(vault, exclude_assessments=True) == _vault_snapshot(initial_vault, exclude_assessments=True)
    _expect(expectations, "dispute preserves every non-assessment file", protected, "Non-assessment snapshot preserved" if protected else "A protected file changed")
    return {"case": "quiz-dispute", "passed": all(item["passed"] for item in expectations), "expectations": expectations}


def _verify_quiz_conflict(
    vault: Path,
    initial_vault: Path | None,
    events: Path | None,
) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    unchanged = bool(initial_vault and _vault_snapshot(vault) == _vault_snapshot(initial_vault))
    response = _final_assistant_text(events)
    reports_conflict = bool(re.search(r"conflict|concurrent|baseline|human edit|reconcile", response, re.IGNORECASE))
    workspace = _workspace_by_name(vault)
    in_progress = bool(
        workspace
        and len(_assessment_files(workspace)) == 1
        and _assessment_status(_read(_assessment_files(workspace)[0])) == "in-progress"
    )
    _expect(expectations, "conflicting recovery preserves the complete vault", unchanged, "Vault snapshot preserved" if unchanged else "Conflict caused a write")
    _expect(expectations, "conflicting assessment remains in progress", in_progress, "Lifecycle remains in-progress" if in_progress else "Lifecycle changed")
    _expect(expectations, "response reports the recovery conflict", reports_conflict, response)
    return {"case": "quiz-conflict", "passed": all(item["passed"] for item in expectations), "expectations": expectations}


def _verify_quiz_ambiguity(vault: Path, initial_vault: Path | None) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    learn = vault / "Learn"
    workspaces = sorted(path for path in learn.iterdir() if path.is_dir()) if learn.is_dir() else []
    assessment_files = [path for workspace in workspaces for path in _assessment_files(workspace)]
    _expect(
        expectations,
        "ambiguous workspaces create no assessment",
        len(workspaces) >= 2 and not assessment_files,
        f"workspaces={[path.name for path in workspaces]}, assessments={[path.name for path in assessment_files]}",
    )
    unchanged = bool(initial_vault and _vault_snapshot(vault) == _vault_snapshot(initial_vault))
    _expect(
        expectations,
        "ambiguity preserves the complete vault",
        unchanged,
        "Vault snapshot preserved" if unchanged else "The vault changed before disambiguation",
    )
    return {
        "case": "quiz-ambiguity",
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
    if case in {"fresh-topic", "partial-resume"}:
        return _verify_workspace(case, vault, initial_vault, research_unavailable)
    if case in QUIZ_CASES:
        return _verify_complete_quiz(case, vault, initial_vault, events)
    if case == "quiz-candidates":
        return _verify_quiz_candidates(vault, initial_vault, events)
    if case == "quiz-in-progress":
        return _verify_quiz_in_progress(vault, initial_vault)
    if case == "quiz-resume":
        return _verify_quiz_resume(vault, initial_vault)
    if case == "quiz-abandon":
        return _verify_quiz_abandon(vault, initial_vault)
    if case == "quiz-interruption":
        return _verify_quiz_interruption(vault, initial_vault, events)
    if case == "quiz-dispute":
        return _verify_quiz_dispute(vault, initial_vault)
    if case == "quiz-conflict":
        return _verify_quiz_conflict(vault, initial_vault, events)
    if case == "quiz-ambiguity":
        return _verify_quiz_ambiguity(vault, initial_vault)
    raise ValueError(f"Unknown case: {case}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Learning OS behavioral eval workspace")
    parser.add_argument(
        "--case",
        required=True,
        choices=[
            "fresh-topic",
            "partial-resume",
            "missing-mission",
            *QUIZ_CASES,
            "quiz-candidates",
            "quiz-in-progress",
            "quiz-resume",
            "quiz-abandon",
            "quiz-interruption",
            "quiz-dispute",
            "quiz-conflict",
            "quiz-ambiguity",
        ],
    )
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
