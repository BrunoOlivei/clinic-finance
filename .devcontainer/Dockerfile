FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# A imagem-base traz um repositório apt do Yarn com chave GPG indisponível
# (NO_PUBKEY) — não usamos Node/Yarn aqui, então removemos antes do update
# pra não derrubar a instalação das libs abaixo.
RUN rm -f /etc/apt/sources.list.d/yarn.list

# Playwright/Chromium runtime deps (browser binary is installed later by
# `playwright install`, this only covers the shared libs it needs to run).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libpango-1.0-0 libcairo2 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

USER vscode
