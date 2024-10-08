deployuser := "ben"
deployto := "$(deployuser)@weatherpi.local"
deploydir := "~/wamotd"

run-local:
	python server.py

deploy:
	rsync --exclude-from=.rsync-excludes -av -e ssh . $(deployto):$(deploydir)
	ssh $(deployto) "sudo cp $(deploydir)/wamotd@.service /etc/systemd/system"
	ssh $(deployto) "cd $(deploydir) && pip install -r requirements.txt"
	ssh $(deployto) "sudo systemctl restart wamotd@$(deployuser).service"

logs:
	ssh $(deployto) "journalctl -u wamotd@$(deployuser).service --since \"1 hour ago\""

check: typecheck format

format:
	python -m black .

typecheck:
	mypy .

venv:
	python3 -m venv .venv
