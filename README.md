# Project Tracker

Jim's project hub, kanban board, R package inventory, and Quarto project log.

## Files

| File | Purpose |
|---|---|
| `index.html` | Navigation and dated project overview |
| `kanban.html` | Four active columns and a collapsible lower-priority backlog; 14 project cards, 13 assessment cards and six Rceattle development cards |
| `project_log.qmd` | Editable log, ten assessment data gaps, completion criteria, and historical project notes |
| `project_log.html` | Rendered project log |
| `packages.html` | Inventory of 22 R packages with repository and documentation links |
| `data/rceattle-tasks.json` | Six Rceattle development task definitions with stable `rceattle-*` identifiers |
| `data/assessment-tasks.json` | Thirteen assessment task definitions with stable `ebs26-*` identifiers |
| `data/assessment-data-gaps.csv` | Ten data tasks with completion criteria |

## Board behavior

Open `kanban.html`, move cards, add notes, or create custom cards. State is saved under the existing `kanban_state` and `kanban_updated` browser-local keys. Saved cards retain their order, column and notes. The October 1 SPoRC priority change moves `c8`, `c9`, `c10` and `c14` into `backlog` once, preserving notes and the saved update timestamp. `kanban_priority_revision` records that migration; later user moves take precedence. Newly supplied cards are appended after saved cards in their initial columns. Custom cards are restored as plain text. State stays in the current browser and site origin; the dated project log is maintained separately.

Initial assessment status on September 29, 2026: eight data tasks and the diagnostics task are To Do; catch extraction, final ATS ages, and the WtAgeRe model update are Waiting; legacy-workspace preservation and repository archival is Done. The 14 earlier project cards are retained. Their published status comes from the historical February 20 log; browser-saved positions take precedence after the one-time SPoRC priority change.

Rceattle cards use teal tags, a teal border and a pale teal background. SPoRC tasks are deferred in the collapsible Lower priority section. Expand it to view notes or drag tasks back into an active column.

## Rceattle development

Six dedicated cards added October 1, 2026 track numerical package-update validation (Done), compiler-warning cleanup (To Do), DSEM documentation and local wiki integration (Done), DSEM covariate evaluation (In Progress), the spmR projection handoff (Waiting), and the 2026 Model 26.0 refit (Waiting). Status comes from saved September 28–29 development records rechecked on October 1. Numerical validation and warning-free compilation have separate tasks. The refit depends on the assessment input tasks and WtAgeRe; the existing Plan Team diagnostics card retains its stable ID and scope.

Keep `data/rceattle-tasks.json`, the six board cards, the hub summary and the Rceattle section of the Quarto log synchronized. Public entries contain task descriptions and status; assessment results, evidence files and drafts remain private. Existing saved positions and notes use the same browser-local keys; the new cards appear automatically when the board loads.

## Assessment checklist

Model 26.0 (Rceattle) is primary, with Model 23.0 for comparison. The ten data tasks cover catch and survey inputs through 2026, BTS and ATS ages through 2026, fishery ages through 2025, biological inputs, ageing error and weights, and a matched input check. Retain actual survey years and the corrected treatment of missing ATS 2020 observations. The public tracker contains task descriptions; assessment results, attachments and draft files remain in the private assessment workspace.

The separate WtAgeRe model-update task (`ebs26-wtage-re`) waits for all four accepted weight-at-age inputs: fishery 2024 and 2025, and survey 2025 and 2026. It feeds the biological-input task; the historical age-error task `c6` remains separate.

Task definitions are recorded in JSON and the ten data gaps in CSV. When a task definition changes, update its board description and the log checklist together. Stable IDs preserve saved browser state.

## Render the log

```bash
quarto render project_log.qmd --to html
```

The log uses semantic Markdown tables and requires no R packages to render. Its YAML includes `lang: en-US` and `lightbox: true`. Commit the editable source and rendered HTML together after review. Package inventory maintenance is documented with its inventory source and build script.


## Refresh the package inventory

Retrieve the public R-universe API response to an ignored local file, then run:

    curl --fail https://jimianelli.r-universe.dev/api/packages -o data/r-universe-source.json
    python3 scripts/build_package_inventory.py data/r-universe-source.json

The current generator records the September 29, 2026 snapshot. Update its snapshot
date when refreshing. Commit the reduced JSON/CSV and packages.html; keep the
full API response local. Build status describes software checks, not scientific
validation. Package filters include records of failed source builds.
