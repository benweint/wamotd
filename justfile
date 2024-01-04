set dotenv-load := true

run-local:
	python server.py

sync:
	rsync --exclude .venv --exclude .mypy --exclude .mypy_cache --exclude .git --exclude __pycache__ -av -e ssh . ben@weatherpi.local:~/wamotd
	ssh ben@weatherpi.local "sudo cp ~/wamotd/wamotd@.service /etc/systemd/system"

deps:
	ssh ben@weatherpi.local "cd ~/wamotd && pip install -r requirements.txt"

restart:
	ssh ben@weatherpi.local "sudo systemctl restart wamotd@ben.service"

format:
	python -m black .

make-venv:
	python3 -m venv .venv

venv:
	. .venv/bin/activate
