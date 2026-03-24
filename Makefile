.PHONY: server client dev dev2

server:
	python -m server.main

client:
	python -m client.main

dev:
	PYTHONUNBUFFERED=1 honcho start

dev2:
	PYTHONUNBUFFERED=1 honcho start --concurrency client=2
