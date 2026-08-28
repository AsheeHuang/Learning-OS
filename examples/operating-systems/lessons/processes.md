# Processes

## Why This Matters

Processes explain how an operating system runs multiple programs while isolating their memory and failures. This supports the mission goal of connecting application behavior to operating-system abstractions.

## Learning Objective

Explain what a process represents and use process isolation to reason about an application failure.

## Explanation

A **program** is executable code stored on disk. A **process** is a running instance of a program together with the state needed to execute it: an address space, CPU state, open resources, and operating-system bookkeeping.

The operating system gives each process the illusion that it has its own memory and CPU. It implements that illusion by virtualizing memory, scheduling CPU time, and controlling access to resources. This isolation means one process normally cannot read or overwrite another process's memory directly.

These abstractions and mechanisms are introduced in [OSTEP's virtualization chapters](https://pages.cs.wisc.edu/~remzi/OSTEP/).

## Example

Two browser tabs may run in separate processes. If one tab crashes because of invalid memory access, process isolation can allow the other tab and the browser's main process to continue running.

## Practice

A text editor opens two documents in one process. Explain which failures process isolation can contain and which failures could still affect both documents.

## Related Concepts

- [[lessons/threads.md|Threads]]
- [[notes/context-switch.md|Context Switch]]
- [[lessons/virtual-memory.md|Virtual Memory]]
- [[lessons/scheduling.md|Scheduling]]

## Sources

- [Operating Systems: Three Easy Pieces — Processes](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
