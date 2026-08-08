---
trigger: always_on
---

# Panel storage sync

## Two locations

- **Git repo** = portable copy for home (no S: on home network). Commit + push materials needed off-campus.
- **Panel share** = `S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others` — department archive; school network only.

## Agent must

1. **Never write to the panel share without explicit user permission** (copy, move, delete).
2. **Never commit** marksheets, grades, student IDs, or bulk student homework submissions.
3. Treat missing git files as unavailable at home — suggest pulling from S: at school, then commit/push.
4. Publish **final deliverables only** to S: (not `_generation/`, `*.spec.json`, drafts).
5. Follow path mapping in `Subjects/STORAGE.md` and skill `panel-storage-sync`.

## When user asks to sync

- **Into repo:** copy selective files S: → `Subjects/…`, then remind or run git commit/push.
- **To panel:** ask permission first; only at school when S: is reachable.
