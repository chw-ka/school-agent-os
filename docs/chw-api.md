# CHW API integration

School data is provided by the separate **[chw-api](https://github.com/chw-ka/chw-api)** repo (deployed at `https://api.chw.edu.hk`). Agents in this repo consume it via MCP or HTTP — do not merge chw-api into school-agent-os.

```
school-agent-os  →  MCP / HTTP  →  chw-api  →  Google Sheets
```

## Cursor MCP setup

Copy `.cursor/mcp.json.example` and set your API key:

```bash
cp .cursor/mcp.json.example ~/.cursor/mcp.json
# Edit X-API-Key: chw_your-key-here
```

Or merge the `chw-api-remote` block into your workspace `.cursor/mcp.json`. Restart MCP in Cursor after changes.

## Kimi Code CLI MCP setup

Copy `.kimi-code/mcp.json.example` to the user or project config location:

```bash
# User-level (shared across repos)
cp .kimi-code/mcp.json.example ~/.kimi-code/mcp.json
# Or project-level (only this repo)
cp .kimi-code/mcp.json.example .kimi-code/mcp.json
# Edit X-API-Key: chw_your-key-here
```

In the Kimi TUI, run `/mcp` to check connection status or `/mcp-config` to manage servers interactively. MCP tools surface as `mcp__chw-api-remote__<tool>`.

## MCP tools (`chw-api-remote`)

| Tool | Use for |
|------|---------|
| `chw_get_students` | List/filter students (class, house, gender) |
| `chw_get_student_by_class_and_number` | One student by class + number |
| `chw_get_student_by_id` | One student by `stuid` |
| `chw_get_teachers` | All teachers |
| `chw_get_teacher` | One teacher by initial |
| `chw_get_classes` | Class ↔ teacher assignments |
| `chw_get_class_info` | Class detail + student list |
| `chw_get_electives` | Elective data |
| `chw_get_student_electives` | One student’s electives |
| `chw_get_split_classes` | Split-class groups |
| `chw_get_student_split_classes` | One student’s groups |
| `chw_get_teacher_subjects` | Teacher–subject–class mappings |
| `chw_get_teacher_subjects_by_teacher` | Subjects for one teacher |
| `chw_get_teacher_subjects_by_class` | Teachers/subjects for one class |
| `chw_get_stats` | School statistics |
| `chw_refresh_data` | Reload from Google Sheets (admin) |

## REST API (direct)

- Docs: `https://api.chw.edu.hk/docs`
- Auth: `X-API-Key` header on every request

## Local development

```bash
# Terminal 1 — sibling chw-api repo
cd ../chw-api && source venv/bin/activate && python main.py

# Terminal 2 — optional local MCP (stdio)
cd ../chw-api && python mcp_server.py
```

## Security

- Never commit API keys. Use `.cursor/mcp.json.example` and `.kimi-code/mcp.json.example` as templates only.
- Prefer per-user keys in MCP `headers` (client-side), not a shared key on the MCP server.

See chw-api `DEPLOYMENT.md` for production MCP deployment.
