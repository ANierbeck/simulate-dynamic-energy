#!/usr/bin/env bash
set -e

echo "Running devcontainer post-create steps..."

# Upgrade pip if available
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --upgrade pip setuptools wheel || true
fi

# Install Python requirements if present
if [ -f "requirements.txt" ]; then
  echo "Installing Python requirements..."
  python3 -m pip install -r requirements.txt || true
fi

# Install node modules if present
if [ -f "package.json" ]; then
  echo "Installing npm packages..."
  npm install || true
fi

if command -v npm >/dev/null 2>&1; then
  echo "Installing GitHub Copilot CLI..."
  npm install -g @githubnext/github-copilot-cli || true
fi

echo "Installing Mistral Vibe..."
curl -LsSf https://mistral.ai/vibe/install.sh | bash || true

echo "Post-create finished."
