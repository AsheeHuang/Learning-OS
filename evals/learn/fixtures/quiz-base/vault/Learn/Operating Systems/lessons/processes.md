# Processes

## Why This Matters

Process isolation shapes production failure boundaries.

## Learning Objective

Explain a process and predict what isolation protects.

## Explanation

A program is passive executable code. A process is one executing instance with its own virtual address space and execution state.[^1]

## Example

Opening the same editor twice creates two processes from one program.

## Practice

1. Compare a program and a process using a new example.
2. Predict what happens when one isolated process crashes.
3. Name one guarantee isolation does not provide.

## Related Concepts

- [[lessons/threads.md|Threads]]

## Sources

[^1]: [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)

## Self-Check Answers

Attempt the questions first.

1. A program is code; a process is a running instance.
2. The operating system can terminate the failed process without allowing it to overwrite another process's private memory.
3. Isolation does not guarantee application-level recovery.
