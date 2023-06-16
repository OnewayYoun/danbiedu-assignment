
dev:
	python danbiedu_assignment/manage.py runserver

docker_compose:
	docker compose -f db/docker-compose.database.yml $(command)

db_up:
	make docker_compose command=up

db_down:
	make docker_compose command=down
