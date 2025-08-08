# Usa la imagen oficial de Odoo 18.0 como base
FROM odoo:18.0

USER root

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-jwt \