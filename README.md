# Obsidian Resurfacer

Daily resurfacing engine for Obsidian vaults, with Python automation.

## Commands

- `make resurface` — Generate resurfacing list.
- `make tag-new-notes` — Tag new notes with #seed.
- `make dry-run-tag-new-notes` — Preview what would be tagged.
- `make clean-resurfacing` — Manual cleanup of resurfacing outputs.
- `make install` — Install Python dependencies with uv.

## .env Setup

Copy `.envs/.env` and set your paths.

## Notes

- Tags used: `#seed`, `#growing`, `#evergreen`
- Resurfacing updates `last-reviewed:` automatically.
- Clean, safe exclusions for system folders.

## Templates

Use your Obsidian Templates folder for:
- New Seed Note
- New Project Note
- Resurfacing Auto Trigger

## Dashboard

Add this to your Control Centre:

```dataview
TABLE file.link AS "Note", created, last-reviewed
FROM "System/Resurfacing"
WHERE file.name = "resurfacing-" + dateformat(date(today), "yyyy-MM-dd") + ".md"
