# Assessment: Processes

- Date: 2026-08-28
- Topics:
  - [[lessons/processes.md|Processes]]

## Questions

### 1. How is a process different from a program?

Prompt:
Explain the distinction in your own words and give an example involving two running instances of the same application.

Learner answer:
A program is executable code stored on disk. A process is one running instance with its own memory and execution state. Opening the same editor twice uses the same program but creates two processes with separate state.

Feedback:
Correct. The answer identifies both the static program and the running instance, then applies the distinction to two instances.

Evidence:
The learner explained the abstraction without repeating the lesson wording and used a valid new example.

Result: strong

### 2. What can process isolation protect in a crash?

Prompt:
A browser runs two tabs in separate processes. One tab performs an invalid memory access. Predict what process isolation can protect and name one thing it cannot guarantee.

Learner answer:
The operating system can terminate the faulty tab process without letting it overwrite the other tab's memory. It cannot guarantee that the whole browser stays useful if the crashed process owned a shared service or important unsaved state.

Feedback:
Correct. The answer applies address-space isolation while avoiding the misconception that process boundaries guarantee complete application-level independence.

Evidence:
The learner transferred the process model to a failure scenario and identified a realistic limitation.

Result: strong

## Misconceptions

No critical misconception observed. Continue distinguishing operating-system isolation from application-level recovery guarantees.

## Summary

The learner accurately explained the process abstraction and applied isolation to an unfamiliar crash scenario.

## Progress Changes

- [[lessons/processes.md|Processes]]: `Needs Validation` → `Mastered`
