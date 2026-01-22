py:
	docker compose up -d --build

rm:
	docker compose down

rpy: rm py