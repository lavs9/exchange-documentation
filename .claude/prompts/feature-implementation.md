# Feature Implementation Prompt Template

When implementing a new feature, provide:

## Context
- Feature name: [e.g., "Search result highlighting"]
- Related component/service: [e.g., "SearchService, SearchBar component"]
- Dependencies: [e.g., "PostgreSQL FTS, react-markdown"]

## Requirements
- [ ] Functional requirement 1
- [ ] Functional requirement 2
- [ ] Non-functional requirements (performance, etc.)

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Implementation Approach
1. Step 1
2. Step 2

## Files to Modify/Create
- [ ] `backend/app/services/search_service.py`
- [ ] `frontend/src/components/SearchBar.tsx`

## Testing Requirements
- Unit tests for [component/function]
- Integration test for [flow]

## Questions/Concerns
- Any technical challenges?
- Need clarification on requirements?

---

**Please follow conventions in `.claude/conventions.md` and reference architecture in `.claude/architecture.md`.**