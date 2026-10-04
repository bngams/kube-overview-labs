# Poste stagiaire "cloud" : VS Code dans le navigateur (code-server) + outils Kubernetes.
# Le démon Docker est fourni par le sidecar DinD (DOCKER_HOST), et k3d y crée le cluster du binôme.
FROM debian:12-slim

ARG CODE_SERVER_VERSION=4.140.0
ARG KUBECTL_VERSION=v1.37.1
ARG K3D_VERSION=v5.9.0
ARG K9S_VERSION=v0.51.0

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates gnupg lsb-release git sudo bash-completion jq nano vim procps \
  && rm -rf /var/lib/apt/lists/*

# --- Docker CLI (le démon est celui du sidecar DinD) ---
RUN install -m 0755 -d /etc/apt/keyrings \
  && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
  && apt-get update && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin docker-buildx-plugin \
  && rm -rf /var/lib/apt/lists/*

# --- kubectl, k3d, k9s ---
RUN ARCH=$(dpkg --print-architecture) \
  && curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl" -o /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl \
  && curl -fsSL "https://github.com/k3d-io/k3d/releases/download/${K3D_VERSION}/k3d-linux-${ARCH}" -o /usr/local/bin/k3d \
  && chmod +x /usr/local/bin/k3d \
  && curl -fsSL "https://github.com/derailed/k9s/releases/download/${K9S_VERSION}/k9s_Linux_${ARCH}.tar.gz" | tar -xz -C /usr/local/bin k9s

# --- code-server (VS Code dans le navigateur) ---
RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --version ${CODE_SERVER_VERSION}

# utilisateur non-root
RUN useradd -m -s /bin/bash student && echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student
USER student
WORKDIR /home/student

# Complétion + alias k (comme sur beaucoup de postes ops)
RUN echo 'source <(kubectl completion bash)' >> ~/.bashrc \
  && echo 'alias k=kubectl' >> ~/.bashrc \
  && echo 'complete -o default -F __start_kubectl k' >> ~/.bashrc

# 13337 (pas 8080) : le poste partage le réseau de son DinD, et les TPs utilisent 8080/8081.
EXPOSE 13337
# PROXY_DOMAIN (ex: lab-kube3-{{port}}.example.com) => https://lab-kube3-8080.example.com sert
# localhost:8080 à la RACINE, derrière l'auth code-server.
CMD ["sh", "-c", "exec code-server --bind-addr 0.0.0.0:13337 --auth password ${PROXY_DOMAIN:+--proxy-domain \"$PROXY_DOMAIN\"}"]
