# Obsidian Resurfacer 🚀

**Purpose:**  
Daily resurfacing system for Obsidian vaults.
Promotes spaced repetition, better note growth, and keeps your vault alive.

> 🌱 seed → 🌿 growing → 🌳 evergreen

## Features

- 🏷️ Auto-tag new notes with `#seed`
- 🧮 Score notes based on age, neglect, and growth stage
- 🗓️ Daily resurfacing output (Markdown)
- 🧼 Manual cleanup of old resurfacing files
- 💡 Safe dry-run mode for checking bulk tags
- 🧩 Fully vault-safe (excludes system folders like `/00/`)

## Commands

| Command                     | Description                              |
|----------------------------|------------------------------------------|
| `make resurface`            | Generate resurfacing list               |
| `make tag-new-notes`        | Tag untagged notes with `#seed`         |
| `make dry-run-tag-new-notes`| Preview new tags safely                 |
| `make clean-resurfacing`    | Manually clean resurfacing outputs      |
| `make install`              | Install Python dependencies via `uv`    |

## Setup

1. Install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```

2. Copy and configure `.env`:
    ```
    VAULT_PATH=/absolute/path/to/vault
    OUTPUT_PATH=/absolute/path/to/vault/Resurfacing
    ```

3. Test run:
    ```bash
    make dry-run-tag-new-notes
    ```

4. When happy, apply tags:
    ```bash
    make tag-new-notes
    ```

5. Generate resurfacing list:
    ```bash
    make resurface
    ```

## Templates

Add these to your Obsidian `/Templates/` folder:

- **New Seed Note.md**
- **New Project Note.md**
- **Resurfacing Auto Trigger.md**

## Dashboard

Add this to your Obsidian Dashboard for live visuals:

```dataview
## 🌱 Notes by Growth Stage

### 🚀 Seeds
TABLE file.link AS "Note", created, last-reviewed
FROM ""
WHERE contains(tags, "seed")
SORT created DESC

### 🌿 Growing Notes
TABLE file.link AS "Note", created, last-reviewed
FROM ""
WHERE contains(tags, "growing")
SORT created DESC

### 🌳 Evergreen Notes
TABLE file.link AS "Note", created, last-reviewed
FROM ""
WHERE contains(tags, "evergreen")
SORT created DESC

