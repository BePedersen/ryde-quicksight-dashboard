# QuickSight Display - Kiosk Mode Dashboard

Selenium-basert applikasjon for fullskjerm-visning av AWS QuickSight-dashboards i kiosk-modus på Raspberry Pi og andre enheter.

## Features

- 🖥️ Fullskjerm visning av QuickSight dashboards
- 🔄 Automatisk reload hver 5. minutt (konfigurerbar)
- 🔐 Persistent login med lagret profil
- 🌆 Støtter 46+ byer med dynamisk byvalg
- 🎨 Tema-bytte basert på tid (light 06:30-22:30, midnight 22:30-06:30)
- ⏰ Automatisk daglig restart (06:30, 14:30, 22:30)
- 📱 Optimalisert for Raspberry Pi

## Krav

### macOS
- Google Chrome (installert)
- Python 3.7+

### Raspberry Pi OS
```bash
sudo apt-get install -y chromium chromium-driver python3 python3-pip
```

## Instalasjon

### 1. Clone repositoriet
```bash
git clone https://github.com/yourusername/quicksight-display.git
cd quicksight-display
```

### 2. Opprett `.env` fil
```bash
cp .env.sample .env
nano .env
```

### 3. Installer Python-pakker
Scriptet installerer automatisk nødvendige pakker (`selenium`, `python-dotenv`) ved første kjøring.

## Konfigurasjon

Redigér `.env` filen:

```ini
# Dashboard-modus: "operations" eller "mechanics"
DASHBOARD_MODE=operations

# Tema (valgfritt): "light" eller "midnight"
# Hvis ikke satt: automatisk bytte basert på tid
THEME=light

# By (se .env.sample for full liste)
CITY=turku

# Refresh-intervall i sekunder
REFRESH_SECS=300

# Login-detaljer
USERNAME=brukernavn@domene.no
PASSWORD=passord
```

## Bruk

### Enkel kjøring
```bash
./scrape_quicksight.py
```

### Med systemctl (Raspberry Pi - auto-start ved boot)
```bash
# Installer service
sudo cp quicksight.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quicksight
sudo systemctl start quicksight

# Sjekk status
sudo systemctl status quicksight

# Se logger
journalctl -u quicksight -f
```

## Støttede Byer

Tilgjengelige byvalg i `CITY`:
asker, bergen, bodø, borås, changzhou, drammen, eskilstuna, fredrikstad, göteborg, halmstad, helsingborg, hämeenlinna, helsinki, hq, joensuu, jyväskylä, karlstad, kristiansand, kuopio, lahti, lappeenranta, linköping, luleå, malmö, moss, norrköping, not used, oslo, oulu, östersund, örebro, pori, sandefjord, seinäjoki, shanghai, skien, stavanger, sundsvall, tampere, trondheim, tromsø, turku, umeå, uppsala, vaasa, västeräs, växjö

## Tema-bytte

- **Automatisk (standard):** Light mode 06:30-22:30, midnight mode 22:30-06:30
- **Manuell:** Sett `THEME=light` eller `THEME=midnight` i `.env` for å låse til ett tema

## Vedlikehold på flere Raspberry Pi-er

### Oppdater kode på alle Pi-er
```bash
./update-all-pis.sh
```

### Sjekk status på alle Pi-er
```bash
./status-all-pis.sh
```

Se `PI_CONFIG.txt` for konfigurasjon av hver Pi.

## Feilsøking

### Ingen innlogging
- Sjekk `USERNAME` og `PASSWORD` i `.env`
- Sjekk at Chrome/Chromium er installert
- Se logs med: `sudo journalctl -u quicksight -f`

### Feil tema eller by
- Sjekk at `CITY` og `THEME` er stavd riktig (små bokstaver)
- Restart service: `sudo systemctl restart quicksight`

### Performance
- Øk `REFRESH_SECS` hvis Pi-en er treg
- Sjekk Chrome cache: `rm -rf /tmp/qschrome-profile` (fjerner lagret profil)

## Lisens

MIT

## Kontakt

benjamin.pedersen@ryde-technology.com
