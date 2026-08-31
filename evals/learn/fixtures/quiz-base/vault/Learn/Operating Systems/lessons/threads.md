# Threads

## Why This Matters

Threads make concurrency cheap but introduce shared-state hazards.

## Learning Objective

Distinguish threads from processes and apply the shared-address-space model.

## Explanation

Threads in one process share an address space and process resources while retaining separate execution state such as stacks and registers.[^1]

## Example

Two worker threads can access one in-memory queue, so their updates require coordination.

## Practice

1. Compare thread and process isolation.
2. Predict a failure caused by unsynchronized shared state.
3. Explain why a thread can be cheaper to create than a process.

## Related Concepts

- [[lessons/processes.md|Processes]]

## Sources

[^1]: [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)

## Self-Check Answers

Attempt the questions first.

1. Threads share a process address space; processes have separate address spaces.
2. Concurrent unsynchronized updates can lose data.
3. Threads reuse process resources.
