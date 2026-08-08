# Migration from Cursor to Qoder

This document records the migration of this project from Cursor IDE configuration to Qoder IDE configuration.

## Migration Date

2026-08-06

## What Changed

### Directory Structure

| Component | Old (Cursor) | New (Qoder) | Status |
|-----------|-------------|-------------|--------|
| Rules directory | `.cursor/rules/*.mdc` | `.qoder/rules/*.md` | ✅ Migrated |
| Skills directory | `.cursor/skills/` | `.qoder/skills/` | ✅ Migrated |
| Project instructions | `CLAUDE.md` | `AGENTS.md` | ✅ Created |
| Constitution | `.cursorrules` | `AGENTS.md` | ✅ Merged into AGENTS.md |

### Rule Files Migrated

All 4 rule files have been migrated with updated frontmatter:

1. **panel-storage-sync.md** — `trigger: always_on` (was `alwaysApply: true`)
2. **subjects-workspace.md** — `trigger: glob, glob: Subjects/**` (was `globs: Subjects/**, alwaysApply: false`)
3. **paper-generator.md** — `trigger: glob, glob: shared-tools/paper-generator/**,...` (was `globs: ..., alwaysApply: false`)
4. **privacy.md** — `trigger: always_on` (was `alwaysApply: true`)

### Skills Migrated

**Personal skills** (copied):
- `cloudsams-browser-login`
- `generate-f5-ict-exam` (+ reference.md)
- `generate-f5-ict-long`
- `generate-f5-ict-mcq`
- `generate-f5-ict-short`
- `mssql-mcp-legacy-execute`
- `panel-storage-sync` (+ mapping.md, scripts/)
- `qef-elearning-grant` (+ reference.md)
- `school-activity-form`
- `student-report-guides`

**Platform skills** (symlinked to `_platform/.cursor/skills/`):
- `meeting-minutes`
- `_template`
- `tidy-up`

Note: Platform skills are still symlinked to `_platform/.cursor/skills/` because the platform repo itself hasn't been migrated yet. This maintains backward compatibility.

### Scripts Updated

- **link-platform.sh** — Now creates symlinks for both `.cursor/` and `.qoder/` directories
  - Keeps `.cursor/` symlinks for backward compatibility (Claude Code, Kimi Code CLI)
  - Adds `.qoder/` symlinks for Qoder IDE

### Documentation Updated

- **docs/PLATFORM-SETUP.md** — Added "Qoder 遷移" section with migration table
- **docs/PLATFORM-COLLABORATION.md** — Updated references from `.cursor/` to `.qoder/`
- **CLAUDE.md** — Added note about Qoder migration; updated skill paths
- **KIMI.md** — Added note about Qoder migration; updated skill paths
- **.cursor/README.md** — Marked as legacy; added migration table
- **README.md** — Updated skill paths
- **Subjects/STORAGE.md** — Updated skill path reference
- **Subjects/README.md** — Updated skill path references

### Skills Internal References Updated

Updated internal references in migrated skills:
- `.qoder/skills/panel-storage-sync/SKILL.md` — Updated script path
- `.qoder/skills/mssql-mcp-legacy-execute/SKILL.md` — Updated MCP config path
- `.qoder/skills/generate-f5-ict-exam/SKILL.md` — Updated rule reference

## Backward Compatibility

The following are preserved for compatibility with other AI tools:

- `.cursor/` directory and all its contents
- `.cursorrules` file
- `CLAUDE.md` file
- `KIMI.md` file
- Symlinks in `.cursor/skills/` pointing to platform skills

## Platform Submodule Note

The `_platform/` submodule still uses `.cursor/` structure. This is intentional for now to maintain compatibility with multiple AI tools (Cursor, Claude Code, Kimi Code CLI). The platform repo will need a separate migration when ready.

Current state:
- Personal repo: `.qoder/` is primary, `.cursor/` is legacy but maintained
- Platform repo: `.cursor/` is still used (not yet migrated)
- Symlinks in personal `.qoder/skills/` point to `_platform/.cursor/skills/`

## Testing Checklist

After migration, verify:

- [x] All rule files exist in `.qoder/rules/` with correct frontmatter
- [x] All personal skills copied to `.qoder/skills/`
- [x] Platform skill symlinks work correctly
- [x] `AGENTS.md` exists at project root
- [x] `link-platform.sh` creates both `.cursor/` and `.qoder/` symlinks
- [x] No broken symlinks in `.qoder/skills/`
- [ ] Test in Qoder IDE (requires manual verification)
- [ ] Verify rules load correctly in Qoder (requires manual verification)
- [ ] Verify skills are discoverable in Qoder (requires manual verification)

## Rollback Plan

If issues arise:

1. The `.cursor/` directory and all original files are preserved
2. Simply revert to using `.cursor/` configuration
3. Delete `.qoder/` directory if needed
4. Remove `AGENTS.md` if needed

## Next Steps

1. **Test in Qoder IDE** — Open project in Qoder and verify rules/skills load correctly
2. **Update team documentation** — Inform colleagues about the migration
3. **Consider platform migration** — When ready, migrate `_platform/` repo to use `.qoder/` structure
4. **Deprecate .cursor/ eventually** — After confirming Qoder works well, consider removing `.cursor/` support (but keep for multi-tool compatibility)

## Related Files

- [docs/PLATFORM-SETUP.md](docs/PLATFORM-SETUP.md) — Setup instructions with Qoder migration notes
- [docs/PLATFORM-COLLABORATION.md](docs/PLATFORM-COLLABORATION.md) — Collaboration guide updated for Qoder
- [AGENTS.md](AGENTS.md) — Main project instructions for Qoder
- [.qoder/rules/](.qoder/rules/) — Qoder rules directory
- [.qoder/skills/](.qoder/skills/) — Qoder skills directory
