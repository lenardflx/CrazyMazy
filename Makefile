.PHONY: server client dev dev2

server:
	python -m server.main

client:
	python -m client.main

dev:
	honcho start

dev2:
	honcho start --concurrency client=2
