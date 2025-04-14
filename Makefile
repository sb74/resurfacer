install:
	uv pip install -r requirements.txt

resurface:
	python3 src/resurfacer.py

clean-resurfacing:
	python3 src/resurfacer.py --clean

tag-new-notes:
	python3 src/resurfacer.py --tag-new-notes

dry-run-tag-new-notes:
	python3 src/resurfacer.py --dry-run-tag-new-notes

