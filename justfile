sync:
	rsync -av -e ssh . ben@weatherpi.local:~/wamotd

format:
	python -m black .
