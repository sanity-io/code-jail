FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Use bash for RUN so we can use pipefail
SHELL ["/bin/bash", "-lc"]

# Create non-root user
RUN useradd -m -s /bin/bash dev \
  && usermod -aG sudo dev \
  && echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Node.js (NodeSource) and codex globally with npm; verify codex is present
RUN set -euo pipefail \
  && apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
  && mkdir -p /etc/apt/keyrings \
  && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
  && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
  && apt-get update \
  && apt-get install -y --no-install-recommends nodejs \
  && npm install -g @openai/codex \
  && codex --version \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER dev
WORKDIR /workspaces
ENV PATH="/usr/local/bin:${PATH}"
