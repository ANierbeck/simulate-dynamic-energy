# ⚡ Dynamische Stromtarif-Analyse

**Eine umfassende Weboberfläche zur Analyse und Optimierung Ihrer Stromkosten mit dynamischen Tarifen**

## 🎯 Zielsetzung

Diese Anwendung hilft Ihnen, Einsparpotenziale durch dynamische Stromtarife zu identifizieren, basierend auf Ihren tatsächlichen Verbrauchsdaten. Besonders geeignet für Haushalte mit:

- **PV-Anlagen** (Solarerzeugung)
- **Batteriespeichern** (SENEC, etc.)
- **Wallboxen** (Elektroauto-Ladung)
- **Wärmepumpen** (Heizenergie)

## 🚀 Schnellstart

### Voraussetzungen
- Python 3.7+
- Streamlit
- InfluxDB v1 oder v2 mit Verbrauchsdaten
- Optional: Dev Container für VS Code

### Installation

```bash
# 1. Virtuelle Umgebung einrichten
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Konfiguration
cp .env.example .env
# .env Datei mit Ihren Zugangsdaten bearbeiten

# 4. Anwendung starten
streamlit run web_app.py --browser.gatherUsageStats=false
```

Die Anwendung öffnet sich automatisch in Ihrem Browser unter `http://localhost:8501`

## 🔧 Konfiguration

Erstellen Sie eine `.env` Datei mit Ihren Einstellungen:

```env
# InfluxDB Konfiguration
INFLUXDB_URL=http://IHRE_INFLUXDB_URL:8086
INFLUXDB_TOKEN=IHR_TOKEN_FALLS_ERFORDERLICH  # Optional - für token-losen Zugriff leer lassen
INFLUXDB_ORG=IHRE_ORGANISATION
INFLUXDB_BUCKET=IHR_DATENBANK_NAME

# Datenquellen (SENEC System)
INFLUXDB_ENTITY_HOUSE_POWER=senec_house_power
INFLUXDB_ENTITY_SOLAR_GENERATED=senec_solar_generated_power
INFLUXDB_ENTITY_BATTERY_POWER=senec_battery_state_power
INFLUXDB_ENTITY_GRID_POWER=senec_grid_state_power

# EPEX Spot Daten
INFLUXDB_MARKET_PRICE=epex_spot_data_market_price
INFLUXDB_TOTAL_PRICE=epex_spot_data_total_price  # Wird verwendet

# Analyseeinstellungen
CURRENT_TARIFF=0.30  # Aktueller Strompreis in €/kWh
ANALYSIS_PERIOD=30d  # Standard-Analysezeitraum
TIMEZONE=Europe/Berlin
DATA_SCALING_FACTOR=1.0  # 1.0 = W, 1000 = Wh zu W
```

## 📊 Unterstützte Datenquellen

### Energiefluss-Daten (SENEC System)
- **Hausverbrauch**: `senec_house_power` - Gesamtverbrauch des Haushalts
- **Solarerzeugung**: `senec_solar_generated_power` - PV-Anlagen-Erzeugung
- **Batterie**: `senec_battery_state_power` - Batterie-Ladezustand und Leistung
- **Netzbezug**: `senec_grid_state_power` - Strom aus dem Netz (wichtig für Tarifvergleich)

### Tarifdaten
- **EPEX Spot**: `epex_spot_data_total_price` - Kundenpreis (nicht Produktionspreis)
- **Zukünftig**: Tiwatt, AWATTAR, Tibber, Rabot Energy, Tado APIs

### Unterstützte InfluxDB-Versionen
- **InfluxDB v1**: Klassische API (kein Flux nötig) - **AKTUELL VERWENDET**
- **InfluxDB v2**: Moderne API mit Flux - **Verfügbar aber nicht aktiv genutzt**
- **Aktuelle Implementierung**: Die Anwendung verwendet ausschließlich die v1 API für bessere Kompatibilität und Einfachheit

## 🎨 Features

### 1. **Echtzeit-Energiefluss-Analyse** ⚡
- Aktueller Verbrauch vs. Solarerzeugung
- Batterie-Ladezustand und Leistung
- Netzbezug (relevant für Tarifvergleich)
- Eigenverbrauchsquote Berechnung

### 2. **Interaktive Zeitrahmenauswahl** 📅
- Letzte 7/30 Tage
- Letzter Monat / Letzte 3 Monate
- Benutzerdefinierter Zeitrahmen
- Auto-Refresh alle 60 Sekunden (konfigurierbar)

### 3. **Echtzeit-Verbrauchsanalyse** 📊
- Gesamtverbrauch in kWh
- Durchschnitts-, Maximal- und Minimalleistung
- Visualisierung des Stromverbrauchs über Zeit
- Kostenberechnung mit aktuellem Tarif

### 4. **Dynamischer Tarifvergleich** 💰
- EPEX Spot Preisanalyse
- Einsparpotenzialberechnung
- Empfehlungssystem (🟢 Wechsel / 🔴 Aktueller Tarif)
- Stündliche Preisvergleiche

### 5. **Zeitperioden-Vergleich** 📈
- Heute vs. Gestern
- Aktuelle Woche vs. Letzte Woche
- Dieser Monat vs. Letzter Monat
- Aktuelles Jahr
- Visualisierung der Verbrauchsmuster

### 6. **Historische & Monatliche Analyse** 📅
- Langfristige Verbrauchstrends
- Saisonale Mustererkennung
- Monatliche Kostenvergleiche
- Jahresübersichten

## 🖥️ Benutzeroberfläche

### Hauptansichten

#### **Energiefluss-Analyse**
![Energiefluss](https://via.placeholder.com/800x400?text=Energiefluss+PV%2FBatterie%2FNetz)
- Zeigt alle Energiequellen und -verbräuche
- Berechnet Eigenverbrauchsquote
- Identifiziert Optimierungspotenziale

#### **Echtzeit-Analyse**
![Echtzeit](https://via.placeholder.com/800x400?text=Aktueller+Verbrauch+%26+Preise)
- Aktuelle Werte und Empfehlungen
- Letzte Stunde / Viertelstunde Statistiken
- Kostenvergleich aktueller Tarif vs. EPEX Spot

#### **Zeitperioden-Vergleich**
![Vergleich](https://via.placeholder.com/800x400?text=Zeitperioden+im+Vergleich)
- Vergleich verschiedener Zeiträume
- Verbrauchsmuster-Analyse
- Kostenentwicklung

#### **Historische Analyse**
![Historisch](https://via.placeholder.com/800x400?text=Historische+Datenanalyse)
- Langfristige Trends
- Saisonale Muster
- Jahresvergleiche

## 🏗️ Architektur

### Modulare Struktur

```
simulate-dynamic-energy/
├── core/                  # Kernmodule (Business Logic)
│   ├── config.py          # Zentralisierte Konfiguration
│   ├── data/              # Datenzugriffsschicht
│   │   ├── influxdb.py    # InfluxDB Integration
│   │   └── providers.py   # Tarif-Provider Daten
│   └── analysis/          # Analysefunktionen
│       ├── consumption.py # Verbrauchsanalyse
│       └── cost.py        # Kostenberechnung
├── web_app.py             # Web-Eintrittspunkt (Streamlit)
├── requirements.txt       # Python-Abhängigkeiten
├── .env.example           # Beispiel-Konfiguration
└── README.md              # Dokumentation
```

### Architekturprinzipien
- **Trennung der Verantwortlichkeiten**: Kernlogik vs. Präsentation
- **Modularität**: Jedes Modul hat klare Verantwortung
- **Wiederverwendbarkeit**: Gemeinsame Logik wird nicht dupliziert
- **Skalierbarkeit**: Einfache Erweiterung um neue Features

## 🔄 Auto-Refresh

Die Anwendung unterstützt automatische Datenaktualisierung:

- **Standardmäßig aktiviert**: Alle 60 Sekunden
- **Konfigurierbar**: Kann in der Sidebar deaktiviert werden
- **Visual Feedback**: Info-Banner zeigt Refresh-Status

```python
# Auto-Refresh Einstellung
auto_refresh_enabled = st.checkbox("Daten alle 60 Sekunden automatisch aktualisieren", value=True)
```

## 📊 Datenanalyse & Berechnungen

### Energieberechnung
Die Anwendung berechnet Energieverbrauch korrekt:

```python
# Energie (kWh) = Leistung (kW) × Zeit (Stunden)
total_consumption_kwh = (average_power_w / 1000) * duration_hours
```

### Kostenberechnung
```python
# Kosten = Verbrauch (kWh) × Preis (€/kWh)
total_cost = total_consumption_kwh * current_tariff
```

### Einsparpotenzial
```python
# Einsparung = Aktuelle Kosten - EPEX Kosten
savings = current_cost - epex_cost
savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
```

## 🔧 Fehlerbehandlung & Tipps

### Häufige Probleme & Lösungen

#### **Problem: Keine Daten gefunden**
**Lösungen:**
- InfluxDB läuft und ist erreichbar
- Datenbank `homeassistant` existiert
- Messung `W` mit den richtigen Entity IDs vorhanden
- Zeitrahmen enthält tatsächlich Daten

#### **Problem: Falsche Skalierung**
**Lösung:**
- Setzen Sie `DATA_SCALING_FACTOR=1000` wenn Daten in Wh statt W
- Standard ist `DATA_SCALING_FACTOR=1.0` für W

## 🔄 Nächste Entwicklungsstufen

### 1. **Echte Tarif-APIs integrieren** 🔌
- Tiwatt API
- AWATTAR API
- Tibber API
- Rabot Energy API
- Tado API

### 2. **Erweiterte Analysefunktionen** 📊
- Historische Datenanalyse über mehrere Jahre
- Saisonale Mustererkennung
- Lastprofiloptimierung
- KI-basierte Vorhersagen

### 3. **Exportfunktionen** 📥
- PDF-Berichte
- CSV-Exporte
- Automatisierte Berichterstellung
- E-Mail-Benachrichtigungen

### 4. **Benachrichtigungssystem** 🔔
- Preisalarme
- Einsparungsbenachrichtigungen
- Optimale Ladezeiten für Wallbox
- Push-Benachrichtigungen

### 5. **API-Schicht** 🌐
- REST API für externe Zugriffe
- JSON-basierte Kommunikation
- Authentifizierung und Autorisierung
- Webhook-Integration

## 🤝 Beitrag & Support

### Wie Sie helfen können
- **Issues melden**: Fehler oder Verbesserungsvorschläge
- **Pull Requests**: Code-Beiträge sind willkommen
- **API-Integrationen**: Besonders gesucht: Echte Tarif-APIs
- **Feedback**: Benutzerfreundlichkeit und Features

### Support
Falls Sie Fragen haben:
1. Überprüfen Sie die Logs in der Konsole
2. Lesen Sie die Fehlermeldungen in der Weboberfläche
3. Fragen Sie nach Hilfe in den Issues

## 📝 Dev Container Unterstützung

Für VS Code Benutzer:

```bash
# Dev Container starten
# Command Palette → Remote-Containers → Reopen in Container

# Oder per CLI:
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .
```

**Features:**
- Python und Node.js vorinstalliert
- GitHub Copilot Integration
- Automatische Abhängigkeiten-Installation
- Mistral-Vibe Unterstützung

## 📋 Changelog & Versionen

### Aktuelle Version
- **Webbasierte Streamlit-Lösung** (keine CLI mehr)
- **Energiefluss-Analyse** (PV + Batterie + Netz + Haus)
- **Auto-Refresh** (60 Sekunden)
- **EPEX Spot Total Price** (realistische Preise)
- **Zeitperioden-Vergleich** (Heute, Gestern, Woche, Monat, Jahr)

### Geplante Versionen
- **v1.1**: Echte Tarif-APIs
- **v1.2**: Exportfunktionen
- **v1.3**: Benachrichtigungssystem
- **v1.4**: API-Schicht

## 📝 Lizenz

**MIT License** - Freie Nutzung, Modifikation und Verteilung

## 🎯 Zielsetzung

Diese Anwendung soll Ihnen helfen:

1. **Transparenz** über Ihre Stromkosten zu erhalten
2. **Einsparpotenziale** durch dynamische Tarife zu identifizieren
3. **Fundierte Entscheidungen** über Tarifwechsel zu treffen
4. **Verbrauchsmuster** zu verstehen und zu optimieren
5. **PV-Anlagen** und Batteriespeicher optimal zu nutzen

Die modulare Architektur ermöglicht schrittweise Verbesserungen und einfache Erweiterung um neue Features.

## 🤖 Entwicklung mit Mistral Vibe

Diese Anwendung wurde mit Unterstützung von **Mistral Vibe** entwickelt:

### Wie Mistral Vibe geholfen hat:

1. **Code-Generierung**: Automatische Generierung von Python-Code für:
   - Datenbank-Integration (InfluxDB)
   - Datenanalyse-Funktionen
   - Weboberfläche (Streamlit)
   - Konfigurationsmanagement

2. **Fehlerbehebung**: Intelligente Fehleranalyse und Lösungsvorschläge für:
   - Zeitstempel-Probleme
   - Daten-Skalierungsprobleme
   - API-Integrationsprobleme
   - Performance-Optimierungen

3. **Dokumentation**: Automatische Generierung von:
   - Code-Kommentaren
   - Docstrings
   - Benutzerdokumentation
   - Konfigurationsanleitungen

4. **Code-Optimierung**: Vorschläge für:
   - Bessere Architektur
   - Performance-Verbesserungen
   - Sicherheitsverbesserungen
   - Wartbarkeitsverbesserungen

5. **Feature-Implementierung**: Unterstützung bei:
   - Energiefluss-Analyse
   - Auto-Refresh-Funktionalität
   - Zeitperioden-Vergleich
   - Daten-Skalierungsfunktionen

### Vorteile der KI-gestützten Entwicklung:

- **Schnellere Entwicklung**: Code-Generierung beschleunigt den Prozess
- **Bessere Qualität**: KI-gestützte Code-Reviews und Optimierungen
- **Weniger Fehler**: Automatische Fehlererkennung und -behebung
- **Bessere Dokumentation**: Automatische Dokumentationsgenerierung
- **Lernfähigkeit**: KI lernt aus dem Code und macht bessere Vorschläge

### Technologien:

- **Mistral Vibe**: KI-gestützte Code-Assistenz
- **Python 3.11**: Moderne Python-Features
- **Streamlit**: Interaktive Weboberfläche
- **InfluxDB**: Zeitreihendatenbank
- **Pandas**: Datenanalyse
- **Plotly**: Interaktive Visualisierungen

## 🎯 Zielsetzung

Diese Anwendung soll Ihnen helfen:

1. **Transparenz** über Ihre Stromkosten zu erhalten
2. **Einsparpotenziale** durch dynamische Tarife zu identifizieren
3. **Fundierte Entscheidungen** über Tarifwechsel zu treffen
4. **Verbrauchsmuster** zu verstehen und zu optimieren
5. **PV-Anlagen** und Batteriespeicher optimal zu nutzen

Die modulare Architektur ermöglicht schrittweise Verbesserungen und einfache Erweiterung um neue Features.

---

**🚀 Viel Erfolg mit Ihrer Stromtarif-Analyse!**

Fragen oder Feedback? Öffnen Sie gerne ein Issue oder Pull Request.
