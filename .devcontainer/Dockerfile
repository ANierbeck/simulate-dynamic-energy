
FROM mcr.microsoft.com/devcontainers/python:0-3.11

# This base image already provides Python 3.11 and common tooling.
ENV DEBIAN_FRONTEND=noninteractive

# Add a few utilities and Node (if you need Node for tooling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential \
    nodejs npm \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

USER vscode
WORKDIR /workspace
