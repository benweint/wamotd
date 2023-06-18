set dotenv-load := true

run-local:
	python server.py

sync:
	rsync -av -e ssh . ben@weatherpi.local:~/wamotd

format:
	python -m black .

make-venv:
	python3 -m venv .venv

venv:
	. .venv/bin/activate
