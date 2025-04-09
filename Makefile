# ollama (intel gpu)
OLLAMA-IGPU-DC = ollama-igpu/docker-compose-ollama.igpu.yml
OLLAMA-IGPU-NAME = ollama-igpu
OLLAMA-IGPU-SERVICE-NAME = ollama-video

# all services
up:
	make up-$(OLLAMA-IGPU-NAME)
	docker exec -it $(OLLAMA-IGPU-SERVICE-NAME) ollama pull llama3.2-vision:11b
	make app-prj
destroy:
	make destroy-$(OLLAMA-IGPU-NAME)
stop:
	make stop-$(OLLAMA-IGPU-NAME)
start:
	make start-$(OLLAMA-IGPU-NAME)

# ollama (intel gpu)
# OLLAMA-IGPU-NAME = ollama
up-$(OLLAMA-IGPU-NAME):
	docker compose -f $(OLLAMA-IGPU-DC) up -d --build --force-recreate
destroy-$(OLLAMA-IGPU-NAME):
	docker compose -f $(OLLAMA-IGPU-DC) down --rmi all --volumes --remove-orphans
stop-$(OLLAMA-IGPU-NAME):
	docker compose -f $(OLLAMA-IGPU-DC) stop
start-$(OLLAMA-IGPU-NAME):
	docker compose -f $(OLLAMA-IGPU-DC) start

# ollama commands
# docker exec -it ollama-video ollama list
# docker exec -it ollama-video ollama pull llama3.2-vision:11b
# docker exec -it ollama-video ollama pull llava:7b
# docker exec -it ollama-video ollama rm llava:7b

# projects (VS Code)
app-prj:
	code app