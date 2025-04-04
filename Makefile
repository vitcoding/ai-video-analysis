# ollama (intel gpu)
OLLAMA-DC = ollama-igpu/docker-compose-ollama.igpu.yml
OLLAMA-NAME = ollama
OLLAMA-SERVICE-NAME = ollama-igpu

# ollama (intel gpu)
# OLLAMA-NAME = ollama
up-$(OLLAMA-NAME):
	docker compose -f $(OLLAMA-DC) up -d --build --force-recreate
destroy-$(OLLAMA-NAME):
	docker compose -f $(OLLAMA-DC) down --rmi all --volumes --remove-orphans
stop-$(OLLAMA-NAME):
	docker compose -f $(OLLAMA-DC) stop
start-$(OLLAMA-NAME):
	docker compose -f $(OLLAMA-DC) start