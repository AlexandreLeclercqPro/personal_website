#!/bin/sh
set -e

DOMAIN="${DOMAIN}"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
EMAIL="${LETSENCRYPT_EMAIL:-}"
STAGING="${LETSENCRYPT_STAGING:-0}"

# Fonction pour vérifier si un certificat Let's Encrypt valide existe
check_valid_cert() {
    if [ -f "$CERT_PATH/fullchain.pem" ]; then
        ISSUER=$(openssl x509 -in "$CERT_PATH/fullchain.pem" -noout -issuer 2>/dev/null || echo "")
        if echo "$ISSUER" | grep -qi "let's encrypt\|R3\|R10\|R11\|E5\|E6"; then
            # Vérifier expiration (plus de 7 jours restants)
            if openssl x509 -in "$CERT_PATH/fullchain.pem" -noout -checkend 604800 2>/dev/null; then
                return 0
            fi
        fi
    fi
    return 1
}

# Attendre que nginx soit prêt
echo "[CERTBOT] Attente de Nginx..."
sleep 10

# Vérifier si un certificat valide existe déjà
if check_valid_cert; then
    echo "[CERTBOT] Certificat Let's Encrypt valide trouvé."
else
    echo "[CERTBOT] Certificat absent ou invalide, demande d'un nouveau certificat..."

    if [ -z "$EMAIL" ]; then
        echo "[CERTBOT] ERREUR: LETSENCRYPT_EMAIL non défini dans .env"
        echo "[CERTBOT] Le site fonctionnera en HTTP uniquement."
    else
        # Options staging
        STAGING_ARG=""
        if [ "$STAGING" = "1" ]; then
            STAGING_ARG="--staging"
            echo "[CERTBOT] Mode STAGING activé"
        fi

        # Nettoyer les anciens certificats temporaires
        rm -rf "$CERT_PATH"
        rm -rf "/etc/letsencrypt/archive/$DOMAIN"
        rm -f "/etc/letsencrypt/renewal/$DOMAIN.conf"

        # Demander le certificat
        certbot certonly --webroot \
            -w /var/www/certbot \
            $STAGING_ARG \
            --email "$EMAIL" \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            -d "$DOMAIN"

        if [ $? -eq 0 ]; then
            echo "[CERTBOT] Certificat obtenu avec succès !"
            echo "[CERTBOT] Nginx rechargera automatiquement dans quelques heures,"
            echo "[CERTBOT] ou exécutez: docker compose exec nginx nginx -s reload"
        else
            echo "[CERTBOT] Échec de l'obtention du certificat."
            echo "[CERTBOT] Vérifiez que le domaine pointe vers ce serveur."
        fi
    fi
fi

# Boucle de renouvellement (toutes les 12h)
echo "[CERTBOT] Démarrage de la boucle de renouvellement..."
trap exit TERM
while :; do
    certbot renew --quiet
    sleep 12h &
    wait $!
done
