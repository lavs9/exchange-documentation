# Refactoring Prompt Template

When refactoring code, provide:

## Refactoring Goal
- What: [e.g., "Extract PDF parsing logic into separate service"]
- Why: [e.g., "Improve testability and separation of concerns"]

## Current State
- Files affected: [List file paths]
- Current issues:
  - [ ] Issue 1 (e.g., "Tight coupling")
  - [ ] Issue 2 (e.g., "Poor testability")

## Desired State
- Target architecture: [Brief description or diagram]
- Benefits:
  - Benefit 1
  - Benefit 2

## Constraints
- [ ] Must maintain backward compatibility
- [ ] No API contract changes
- [ ] Performance must not degrade
- [ ] All tests must pass

## Migration Path
1. Step 1: [e.g., "Create new service interface"]
2. Step 2: [e.g., "Migrate existing code"]
3. Step 3: [e.g., "Update tests"]
4. Step 4: [e.g., "Remove deprecated code"]

## Testing Strategy
- [ ] All existing tests pass
- [ ] Add tests for new structure
- [ ] Performance benchmarks remain stable

---

**Please follow architecture patterns in `.claude/architecture.md` and conventions in `.claude/conventions.md`.**