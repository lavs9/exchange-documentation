# Bug Fix Prompt Template

When fixing a bug, provide:

## Bug Description
- Summary: [One-line description]
- Severity: [Critical/High/Medium/Low]
- Component affected: [e.g., "DocumentViewer component"]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Expected: [what should happen]
4. Actual: [what actually happens]

## Error Messages/Logs
[Paste error messages or logs here]

## Hypothesis
- Potential cause: [Your theory about the bug]
- Related code: [File paths and line numbers]

## Environment
- OS: [e.g., Ubuntu 22.04]
- Browser (if frontend): [e.g., Chrome 120]
- Docker version: [e.g., 24.0.6]

## Investigation Done
- [ ] Checked logs
- [ ] Reproduced locally
- [ ] Reviewed recent changes
- [ ] Checked similar issues

## Fix Requirements
- [ ] Must not break existing functionality
- [ ] Should include test to prevent regression
- [ ] Update documentation if behavior changes

---

**Please provide root cause analysis and fix following `.claude/conventions.md`.**