# AGENTS.md — Master Engineering Contract for THREAD Runtime

This file is the authoritative engineering contract governing all development, architecture, and AI-assisted workflows within the `THREAD Runtime` repository.

---

## 1. PRODUCT VISION

THREAD is a lightweight, portable, offline-first cinematic story runtime.

* **Offline Customer Product**: The customer-facing runtime operates completely offline without network dependencies or AI services.
* **AI as Accelerator Only**: AI tools (e.g. Antigravity) are development accelerators only, not runtime dependencies.
* **Core Product Goals**:
  * Load reusable story/content packages.
  * Execute interactive narrative experiences.
  * Support local save and resume functionality.
  * Detect platform capabilities and adapt presentation to available resources.
  * Maintain smoothness on low-spec hardware and higher fidelity on high-spec hardware.
  * Separate runtime engine code strictly from story content packages.
  * Support multiple independent story packages.
  * Maintain cross-platform portability across operating systems and hardware classes.
  * Deliver a self-contained, commercially distributable runtime executable.

---

## 2. CORE ENGINEERING PHILOSOPHY

When trade-offs arise, prioritize in this order:

1. **Correctness**
2. **Reliability**
3. **Simplicity**
4. **Portability**
5. **Performance Efficiency**
6. **Cost Efficiency**
7. **Maintainability**
8. **Reusability**
9. **Security**
10. **Development Speed**

* Never sacrifice actual reliability for theoretical capability.
* Prefer the smallest viable architecture that satisfies current requirements.

---

## 3. RESOURCE-ADAPTIVE PRINCIPLE

THREAD must degrade gracefully when system resources are constrained. The degradation priority cascade is:

```text
DO NOT CRASH
    ↓
DO NOT HANG
    ↓
DO NOT STUTTER
    ↓
PRESERVE STORY INTEGRITY
    ↓
PRESERVE AUDIO
    ↓
PRESERVE VISUAL FIDELITY
```

* Weaker hardware receives lower-fidelity presentation, never a crash, freeze, or stutter.
* Stronger hardware receives enhanced visual/audio fidelity.
* Never make high-end hardware a requirement for basic story playback unless explicitly justified.

---

## 4. PORTABILITY PRINCIPLE

Architectural portability and verified compatibility are distinct concepts.

* Never claim platform support (Linux, Windows, Android, ARM, handhelds, consoles, GPU acceleration) without explicit recorded test verification.
* Use explicit compatibility states:
  * `VERIFIED`
  * `LIMITED`
  * `UNSUPPORTED`
  * `NOT TESTED`

---

## 5. AI PRINCIPLE

* AI is strictly a development accelerator.
* The customer runtime must **never** require:
  * Gemini, OpenAI, Claude, Groq, Hugging Face, Ollama
  * API keys or user AI accounts
  * Cloud inference or active network connectivity
* All AI-generated code is untrusted and requires unit testing and code review.

---

## 6. DEPENDENCY PRINCIPLE

Default selection hierarchy:
```text
Python Standard Library  >  Small Focused Dependency  >  Large Framework
```

Before adding any dependency, evaluate:
* Functionality gained, package size, performance impact, portability, license, maintenance health, security risk, and standard library alternatives.
* Never add a dependency merely for convenience.

---

## 7. ARCHITECTURE PRINCIPLE

* Maintain clear, decoupled module and service boundaries.
* **No Premature Microservices**: Prefer local Python modules and standard process boundaries until scale explicitly requires separate services.
* Avoid Kubernetes, k3s, cloud infrastructure, external databases, message queues, or distributed systems unless concrete requirements demand them.

---

## 8. DATA PRINCIPLE

* Story content must be strictly separated from runtime code.
* A story package must be portable, versioned, validated, self-contained, offline-capable, and license-aware.
* Treat story packages as validated data, never as executable code.

---

## 9. SECURITY PRINCIPLE

* Never commit secrets, API keys, or embedded credentials.
* Validate all story package input before parsing.
* Never execute untrusted story content as arbitrary code.
* Never silently download executable dependencies or contact remote services.

---

## 10. GIT PRINCIPLE

* Git is the primary recovery mechanism.
* Check repository status (`git status`) before and after significant work.
* Never automatically execute `git reset --hard`, `git clean -fd`, or `git push --force`.
* Do not create commits or push to remote repositories unless explicitly instructed by the user.

---

## 11. TESTING PRINCIPLE

Validation hierarchy:
```text
Unit Test  →  Integration Test  →  CLI / Manual Smoke Test  →  Performance / Resource Test
```

* Every feature must have a verification strategy.
* A feature is done only when its acceptance criteria are demonstrably satisfied by test execution.

---

## 12. PERFORMANCE PRINCIPLE

* Measure before optimizing.
* Record execution time, memory usage, disk footprint, CPU/GPU utilization, startup latency, and failure behavior.
* Optimize actual measured bottlenecks, not theoretical assumptions.

---

## 13. FAILURE PRINCIPLE

Every subsystem must define:
* Normal behavior
* Invalid input behavior
* Missing resource behavior
* Unavailable capability behavior
* Corrupted data behavior
* Resource exhaustion behavior

Prefer graceful degradation over undefined behavior.

---

## 14. DEVELOPMENT PRINCIPLE

Work in small vertical increments:
```text
Tiny Working Capability  →  Test  →  Integrate  →  Measure  →  Checkpoint  →  Next Capability
```

Do not build speculative frameworks or unneeded abstractions.

---

## 15. AGENT BEHAVIOR CONTRACT

### Before Modifying Code
1. Inspect relevant repository state.
2. Understand existing implementation & dependencies.
3. Identify acceptance criteria.
4. Plan the smallest viable change.

### While Modifying Code
* Preserve existing behavior and localize changes.
* Avoid unrelated refactorings or unneeded dependencies.
* Add unit tests along with features.
* Stop when the requested objective is satisfied.

### After Modifying Code
1. Run relevant tests & test suite.
2. Run CLI smoke tests.
3. Execute `git diff --check` and inspect `git diff`.
4. Report exactly what changed.
* **Stop and report** if requirements conflict or an irreversible decision is required.

---

## 16. TASK EXECUTION CONTRACT

Every task execution should adhere to the following schema:
* `PURPOSE`: Objective of the task.
* `INPUTS`: Required inputs and configuration.
* `CONTEXT`: Background knowledge and state.
* `CONSTRAINTS`: Boundaries and limitations.
* `INVARIANTS`: Conditions that must remain true.
* `ALLOWED ACTIONS`: Explicitly permitted operations.
* `FORBIDDEN ACTIONS`: Explicitly prohibited operations.
* `ACCEPTANCE CRITERIA`: Verifiable success conditions.
* `VALIDATION`: Testing strategy.
* `FAILURE CONDITIONS`: Conditions defining failure.
* `OUTPUT`: Expected deliverables.

---

## 17. FINAL REPORT CONTRACT

After every task completion, return a report with the following structure:

### Changed
Files modified and rationale.

### Tests
Exact commands executed and output results.

### Behavior
What now works or changed.

### Dependencies
Added/removed/changed dependencies.

### Compatibility
What platforms/configurations were actually tested.

### Risks
Remaining risks with severity classification.

### Git
Current git status and confirmation that no unauthorized commits/pushes occurred.

### Recommended Next Step
Exactly ONE next action.
