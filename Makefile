.PHONY: dev down logs test shell

dev:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest backend/tests/

shell:
	docker-compose exec backend /bin/bash
