# Dev Container — Kurzanleitung

Öffne das Projekt in VS Code und wähle **Remote-Containers: Reopen in Container** (oder Command Palette → Remote-Containers).

Dateien:
- `.devcontainer/Dockerfile` — Image mit Python und Node
- `.devcontainer/devcontainer.json` — Devcontainer-Konfiguration
- `.devcontainer/postCreate.sh` — Installiert Abhängigkeiten falls vorhanden

Zusätzliche Tools:
- Die VS Code Extension `GitHub.copilot` ist in der Devcontainer-Config eingetragen.
- Das `postCreate`-Script versucht, die GitHub Copilot CLI zu installieren (`@githubnext/github-copilot-cli`).
- Das `postCreate`-Script führt außerdem das Mistral-Vibe-Installationsscript aus:

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

Hinweis: Du hast „cline" erwähnt — welche konkrete CLI oder welches Tool genau meinst du damit? Dann kann ich es automatisch mitinstallieren.

Bauen & Starten (lokal, falls Docker läuft):

1. In VS Code: Command Palette → Remote-Containers → Reopen in Container
2. Oder per CLI (devcontainer CLI installiert):
```
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .
```

Anpassungen: Passe `devcontainer.json` an, um zusätzliche Extensions, Forwarded Ports oder `settings` hinzuzufügen.
