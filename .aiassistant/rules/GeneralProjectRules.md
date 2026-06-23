---
apply: always
---

ARCHITECTURE PRINCIPLES:
- Keep business logic separate from I/O layers
- Avoid circular dependencies
- Prefer explicit interfaces over implicit coupling

CODE STYLE:
- Favor small pure functions
- Explicit error handling required
- No hidden side effects in core logic

CHANGE POLICY:
- Minimize diff size
- Prefer surgical changes over rewrites
- Do not refactor unrelated code during feature work

TESTING EXPECTATIONS:
- New logic must be testable in isolation
- Critical paths must have unit tests

AI USAGE POLICY:
- AI should propose plans before implementation
- AI should not refactor beyond requested scope