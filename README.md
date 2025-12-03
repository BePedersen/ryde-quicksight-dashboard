# ryde-quicksight-dashboard

Selenium-basert applikasjon for fullskjerm-visning av AWS QuickSight-dashboards i kiosk-modus på Raspberry Pi og andre enheter.

## Features

- 🖥️ Fullskjerm visning av QuickSight dashboards
- 🔄 Automatisk reload hver 5. minutt (konfigurerbar)
- 🔐 Persistent login med lagret profil
- �� Støtter 46+ byer med dynamisk byvalg
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
git clone https://github.com/BePedersen/ryde-quicksight-dashboard.git
cd ryde-quicksight-dashboard
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
# THEME=light

# By (se .env.sample for full liste)
CITY=turku

# Refresh-intervall i sekunder
REFRESH_SECS=300

# Login-detaljer
USERNAME=brukernavn@domene.no
PASSWORD=passord
```

## Bruk

### Kjør lokalt på Mac/Linux
```bash
./scrape_quicksight.py
```

### Kjør på Raspberry Pi med systemctl (auto-start ved boot)

Se "Raspberry Pi 5 - Installasjon og Konfiguration" seksjonen over for full installasjonsguide.

**Kort oppsummering:**
- Pi-en kjører automatisk som systemctl service
- Autostartes ved reboot
- Administreres via Pi Connect Remote shell

## Raspberry Pi 5 - Installasjon og Konfiguration

### Installasjon via Pi Connect (Remote shell)

```bash
# Clone repo
cd /home/pi
git clone https://github.com/BePedersen/ryde-quicksight-dashboard.git quicksight
cd quicksight

# Opprett .env og rediger CITY
cp .env.sample .env
nano .env  # Rediger CITY, THEME, DASHBOARD_MODE, etc.

# Installer Python-pakker
pip install -r requirements.txt

# Lag systemctl service
sudo bash -c 'cat > /etc/systemd/system/quicksight.service << EOF
[Unit]
Description=AWS QuickSight Dashboard Display
After=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/quicksight
ExecStart=/usr/bin/python3 /home/pi/quicksight/scrape_quicksight.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
'

# Enable og start service
sudo systemctl daemon-reload
sudo systemctl enable quicksight
sudo systemctl start quicksight

# Sjekk at det kjører
sudo systemctl status quicksight
```

### Vedlikehold via Pi Connect

**Endre konfigurasjon:**
```bash
# Rediger .env
nano /home/pi/quicksight/.env

# Restart service
sudo systemctl restart quicksight
```

**Sjekk status:**
```bash
# Se live logs
sudo journalctl -u quicksight -f

# Sjekk service status
sudo systemctl status quicksight
```

**Stopp/Start service:**
```bash
# Stopp
sudo systemctl stop quicksight

# Start
sudo systemctl start quicksight

# Restart
sudo systemctl restart quicksight
```

### Oppdater kode fra GitHub

```bash
cd /home/pi/quicksight
git pull
sudo systemctl restart quicksight
```

## Støttede Byer

Tilgjengelige byvalg i `CITY`:
asker, bergen, bodø, borås, changzhou, drammen, eskilstuna, fredrikstad, göteborg, halmstad, helsingborg, hämeenlinna, helsinki, hq, joensuu, jyväskylä, karlstad, kristiansand, kuopio, lahti, lappeenranta, linköping, luleå, malmö, moss, norrköping, not used, oslo, oulu, östersund, örebro, pori, sandefjord, seinäjoki, shanghai, skien, stavanger, sundsvall, tampere, trondheim, tromsø, turku, umeå, uppsala, vaasa, västeräs, växjö

## Tema-bytte

- **Automatisk (standard):** Light mode 06:30-22:30, midnight mode 22:30-06:30
- **Manuell:** Sett `THEME=light` eller `THEME=midnight` i `.env` for å låse til ett tema

## Vedlikehold på flere Raspberry Pi-er

### Endre konfigurasjon via Pi Connect

Hver Pi administreres individuelt via Pi Connect:

1. **Åpne Pi Connect**
2. **Klikk på ønsket Pi-enhet**
3. **Velg "Remote shell"**
4. **Gjør endringer:**
   ```bash
   nano /home/pi/quicksight/.env
   sudo systemctl restart quicksight
   ```

### Batch oppdateringer

Hvis du trenger å oppdatere flere Pi-er samtidig, kan du:

```bash
# SSH inn på hver Pi (via Remote shell)
cd /home/pi/quicksight
git pull
sudo systemctl restart quicksight
```

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
