set dotenv-load := true

run-local:
	python code.py

sync:
	rsync -av -e ssh . ben@weatherpi.local:~/wamotd

format:
	python -m black .
