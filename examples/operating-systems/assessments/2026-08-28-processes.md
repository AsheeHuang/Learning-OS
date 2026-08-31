# Assessment: Processes

- Date: 2026-08-28
- Status: complete
- Topics:
  - [[lessons/processes.md|Processes]]

## Topic: Processes

- Path: lessons/processes.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-25
- Starting Last Tested: —

### Question 1: Process and program

Source section: ## Explanation
Prompt: In your own words, what is the difference between a program and a process?

Learner answer:
A program is executable code stored on disk. A process is one running instance with its own memory and execution state. Opening the same editor twice uses the same program but creates two processes with separate state.

Feedback:
Correct. The answer identifies both the static program and the running instance, then applies the distinction to two instances.

Evidence:
The learner explained the abstraction without repeating the lesson wording and supplied a valid new example.

Expected key points:
A program is passive code; a process is an executing instance with runtime state. One program can have multiple independent process instances.

Result: strong

### Question 2: Isolation in a crash

Source section: ## Example
Prompt: If one browser-tab process crashes, what does process isolation protect in the other tab?

Learner answer:
The operating system can terminate the faulty tab process without letting it overwrite the other tab's memory. It cannot guarantee that the whole browser stays useful if the crashed process owned a shared service or important unsaved state.

Feedback:
Correct. The answer applies address-space isolation while avoiding the misconception that process boundaries guarantee complete application-level independence.

Evidence:
The learner transferred the process model to a failure scenario and identified a realistic limitation.

Expected key points:
Isolation protects another process's address space; it does not guarantee application-level recovery or preserve dependencies and unsaved state.

Result: strong

### Topic Outcome

Grounding: verified
Result: strong
Evidence summary: The learner independently distinguished programs from processes and transferred process isolation to an unfamiliar failure scenario without a critical misconception.

## Misconceptions

No critical misconception observed. Continue distinguishing operating-system isolation from application-level recovery guarantees.

## Summary

Processes has grounded, independent recall and transfer evidence.

## Progress Changes

- [[lessons/processes.md|Processes]]: `Needs Validation` → `Mastered`
