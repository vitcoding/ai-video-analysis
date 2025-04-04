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

# ollama commands
# docker exec -it ollama-video ollama list
# docker exec -it ollama-video ollama pull llava:7b
# docker exec -it ollama-video ollama rm llava:7b

# projects
app-prj:
	codium app