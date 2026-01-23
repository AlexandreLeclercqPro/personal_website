# ============================================
# DÉVELOPPEMENT (local, sans SSL)
# ============================================

dev:
	docker compose -f docker-compose.dev.yml up -d --build

dev-down:
	docker compose -f docker-compose.dev.yml down

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

dev-restart: dev-down dev

# ============================================
# PRODUCTION (serveur, avec SSL)
# ============================================

prod:
	docker compose up -d --build

prod-down:
	docker compose down

prod-logs:
	docker compose logs -f

prod-restart: prod-down prod

# Première installation SSL (à exécuter sur le serveur)
prod-init: init-ssl prod

init-ssl:
	./init-letsencrypt.sh

# Renouvellement manuel des certificats
renew-ssl:
	docker compose run --rm certbot renew
	docker compose exec nginx nginx -s reload

reload-nginx:
	docker compose exec nginx nginx -s reload
