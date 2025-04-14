import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import frontmatter

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/run.log", mode="a")],
)
logger = logging.getLogger(__name__)

# --- Load .env Variables ---
load_dotenv(dotenv_path=Path(".envs/.env"))

VAULT_PATH = Path(os.getenv("VAULT_PATH")).resolve()
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH")).resolve()
RESURFACING_COUNT = int(os.getenv("RESURFACING_COUNT", 5))
TAG_WEIGHTS = {
    "seed": int(os.getenv("SEED_WEIGHT", 3)),
    "growing": int(os.getenv("GROWING_WEIGHT", 2)),
    "evergreen": int(os.getenv("EVERGREEN_WEIGHT", 1)),
}
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 7))

# Excluded folders and files for tagging and processing
EXCLUDED_PATHS = [
    "System",
    "Templates",
    "Daily",
    "Journals",
    "Work Notes",
    "Inbox",
    "00",
    "Dashboard.md",
]

# --- Constants ---
TODAY = datetime.now().date()
TARGET_FILENAME = f"resurfacing-{TODAY}.md"

# --- Utility Functions ---


def safe_note_paths():
    """Yield only non-excluded .md files in the vault, skipping excluded directories properly."""
    excluded_paths = [VAULT_PATH / Path(excluded) for excluded in EXCLUDED_PATHS]
    for root, dirs, files in os.walk(VAULT_PATH):
        root_path = Path(root).resolve()
        # Skip the root folder if it's excluded
        if any(
            root_path == excluded or root_path.is_relative_to(excluded)
            for excluded in excluded_paths
        ):
            continue
        # Prune excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                (root_path / d).resolve() == excluded
                or (root_path / d).resolve().is_relative_to(excluded)
                for excluded in excluded_paths
            )
        ]
        for file in files:
            if file.endswith(".md"):
                yield Path(root) / file


def parse_note_metadata(note_path):
    try:
        post = frontmatter.load(note_path)
        metadata = post.metadata
        tags = metadata.get("tags", [])
        created = metadata.get("created")
        last_reviewed = metadata.get("last-reviewed")

        if isinstance(tags, str):
            tags = [tags]

        if not created:
            created = datetime.fromtimestamp(note_path.stat().st_ctime).date()
        else:
            created = datetime.strptime(created, "%Y-%m-%d").date()

        if last_reviewed:
            last_reviewed = datetime.strptime(last_reviewed, "%Y-%m-%d").date()
        else:
            last_reviewed = created

        return {
            "path": note_path,
            "tags": tags,
            "created": created,
            "last_reviewed": last_reviewed,
        }

    except Exception as e:
        logger.warning(f"Failed to parse {note_path}: {e}")
        return None


def calculate_score(note):
    tag_score = max((TAG_WEIGHTS.get(tag, 0) for tag in note["tags"]), default=0)
    age_days = (TODAY - note["created"]).days
    neglect_days = (TODAY - note["last_reviewed"]).days
    return tag_score * (age_days + neglect_days)


def update_last_reviewed(note):
    try:
        post = frontmatter.load(note["path"])
        post.metadata["last-reviewed"] = TODAY.strftime("%Y-%m-%d")
        with open(note["path"], "w") as f:
            f.write(frontmatter.dumps(post))
        logger.info(f"Updated last-reviewed for {note['path'].name}")
    except Exception as e:
        logger.error(f"Failed to update {note['path']}: {e}")


def add_seed_tag_to_notes(dry_run=False):
    for note_path in safe_note_paths():
        post = frontmatter.load(note_path)
        tags = post.metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if not any(tag in TAG_WEIGHTS for tag in tags):
            if dry_run:
                logger.info(f"[Dry Run] Would add #seed tag to: {note_path}")
            else:
                tags.append("seed")
                post.metadata["tags"] = tags
                if not post.metadata.get("created"):
                    post.metadata["created"] = TODAY.strftime("%Y-%m-%d")
                if not post.metadata.get("last-reviewed"):
                    post.metadata["last-reviewed"] = TODAY.strftime("%Y-%m-%d")
                with open(note_path, "w") as f:
                    f.write(frontmatter.dumps(post))
                logger.info(f"Added #seed tag to {note_path}")


# --- Core Functions ---


def collect_notes():
    notes = []
    for path in safe_note_paths():
        note_data = parse_note_metadata(path)
        if note_data and any(tag in note_data["tags"] for tag in TAG_WEIGHTS):
            notes.append(note_data)

    logger.info(f"Collected {len(notes)} notes for resurfacing consideration.")
    return notes


def generate_resurfacing_list(notes):
    notes.sort(key=calculate_score, reverse=True)
    selected = notes[:RESURFACING_COUNT]
    for note in selected:
        update_last_reviewed(note)
    return selected


def write_markdown_output(selected_notes):
    output_lines = [f"# 🌿 Resurfacing Notes for {TODAY}\n"]

    sections = {"seed": [], "growing": [], "evergreen": []}

    for note in selected_notes:
        relative_path = note["path"].relative_to(VAULT_PATH)
        link = f"[[{relative_path}]]"
        line = f"- {link} (Created: {note['created']}, Last Reviewed: {note['last_reviewed']})"

        for tag in TAG_WEIGHTS:
            if tag in note["tags"]:
                sections[tag].append(line)

    for section, lines in sections.items():
        if lines:
            output_lines.append(f"\n## {section.capitalize()} Notes\n")
            output_lines.extend(lines)

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_PATH / TARGET_FILENAME
    output_file.write_text("\n".join(output_lines))
    logger.info(f"Resurfacing list written to {output_file}")


def clean_old_outputs():
    cutoff = TODAY - timedelta(days=RETENTION_DAYS)
    for file in OUTPUT_PATH.glob("resurfacing-*.md"):
        try:
            date_str = file.stem.replace("resurfacing-", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if file_date < cutoff:
                file.unlink()
                logger.info(f"Deleted old resurfacing file: {file.name}")
        except Exception as e:
            logger.warning(f"Failed to process {file.name}: {e}")


# --- Main Execution ---

if __name__ == "__main__":
    import sys

    if "--clean" in sys.argv:
        clean_old_outputs()
    elif "--tag-new-notes" in sys.argv:
        add_seed_tag_to_notes(dry_run=False)
        logger.info("Tagging complete.")
    elif "--dry-run-tag-new-notes" in sys.argv:
        add_seed_tag_to_notes(dry_run=True)
        logger.info("Dry run tagging complete.")
    else:
        notes = collect_notes()
        selected = generate_resurfacing_list(notes)
        write_markdown_output(selected)
        logger.info("Resurfacing complete.")
