## Qoder Skills (daily workflows)

Skills in **`.qoder/skills/`** fall into two layers:

- **Platform** (from `_platform/` submodule): `meeting-minutes`, `tidy-up`, `_template` — symlinked after `./scripts/link-platform.sh`
- **Personal** (this repo only): `panel-storage-sync`, `generate-f5-ict-*`, `qef-elearning-grant`, etc.

### Add a personal workflow

1. Create `./.qoder/skills/{kebab-name}/SKILL.md`
2. Use `.qoder/skills/_template` (platform) as a starting point
3. Keep subject-specific paths out of platform skills

### Add a shared (platform) workflow

1. Edit in `_platform/.qoder/skills/` and commit in **school-agent-os-platform** repo
2. Bump submodule in this repo, or open a PR to platform

See [docs/PLATFORM-SETUP.md](../../docs/PLATFORM-SETUP.md).
