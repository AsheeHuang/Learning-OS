# Threads

## Why This Matters

Threads let one process make progress on multiple activities, but shared memory introduces coordination risks that application developers must understand.

## Learning Objective

Explain what threads share, what remains private to each thread, and why shared state requires synchronization.

## Explanation

Threads in the same process share the process's address space and resources such as open files. Each thread has its own execution state, including a program counter, registers, and stack.

Sharing makes communication inexpensive: one thread can write data that another thread reads. The same property creates races when operations interleave in an unexpected order. Synchronization mechanisms such as locks constrain those interleavings.

OSTEP introduces threads and their shared-state hazards in its [concurrency chapters](https://pages.cs.wisc.edu/~remzi/OSTEP/).

## Example

Two threads increment the same counter. If each increment reads, modifies, and writes separately, both threads can read the same old value and one increment can be lost.

## Practice

Compare two threads in one process with two separate processes. Identify one benefit and one risk of the shared address space.

## Related Concepts

- [[lessons/processes.md|Processes]]
- [[lessons/locks.md|Locks]]
- [[notes/context-switch.md|Context Switch]]

## Sources

- [Operating Systems: Three Easy Pieces — Concurrency](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf)
