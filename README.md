# Project Tracker

Jim's project kanban board and living project log.

## Files

| File | Description |
|------|-------------|
| `kanban.html` | Interactive drag-and-drop kanban board — open in any browser |
| `project_log.qmd` | Quarto project log with sub-task checklists and weekly check-in template |

## Usage

**Kanban board:** Open `kanban.html` in a browser. Drag cards between columns, add notes, add new cards. State saves to browser local storage.

**Project log:** Edit `project_log.qmd` directly, adding dated progress notes as you work. Render with:

```bash
quarto render project_log.qmd
```

## Sharing

Share the rendered `project_log.html` (or PDF) with colleagues, or invite them to clone this repo and open `kanban.html` locally.

## Workflow tip

Commit changes to `project_log.qmd` regularly — the git history becomes your progress record.
