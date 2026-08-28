# Context Switch

Source: [[lessons/processes.md|Processes]]

## Question

What does the operating system save and restore when it switches execution from one process or thread to another, and why does that switching have a cost?

## Explanation

A context switch changes which execution context is using a CPU. The operating system preserves enough state to resume the outgoing task later and restores the incoming task's saved state. This includes CPU registers, the program counter, the stack pointer, and scheduling metadata. A switch between processes may also change the active address-space context.

The cost is not limited to saving and restoring registers. The incoming task may have colder CPU caches or translation state, so useful work can slow down after the switch. OSTEP discusses the mechanism when explaining limited direct execution and scheduling ([source](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)).

## Connection to the Source

[[lessons/processes.md|Processes]] describes the abstraction of a running program. A context switch is one mechanism that lets several process or thread abstractions share a smaller number of CPUs.

## Related Concepts

- [[lessons/threads.md|Threads]]
- [[lessons/scheduling.md|Scheduling]]
- [[lessons/virtual-memory.md|Virtual Memory]]

## Sources

- [Operating Systems: Three Easy Pieces — Mechanism: Limited Direct Execution](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
