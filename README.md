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
- 🩺 Dashboard health check med auto-restart ved feil

## Krav

## update and restart command
cd ~/ryde-quicksight-dashboard
curl -o scraper.py https://raw.githubusercontent.com/BePedersen/ryde-quicksight-dashboard/main/scraper.py
sudo systemctl restart ryde-quicksight-dashboard

### macOS
- Google Chrome (installert)
- Python 3.7+

### Raspberry Pi OS
```bash
sudo apt-get install -y chromium chromium-driver python3 python3-pip
```

### Installer Apple-emojier på Raspberry Pi 5

Raspberry Pi OS viser ikke emojier som standard. Slik installerer du Apple Color Emoji-font:

```bash
# Installer avhengigheter
sudo apt-get install -y fontconfig

# Last ned Apple Color Emoji-font
wget -q https://github.com/samuelngs/apple-emoji-linux/releases/latest/download/AppleColorEmoji.ttf -O /tmp/AppleColorEmoji.ttf

# Installer fonten
sudo mkdir -p /usr/local/share/fonts/apple-emoji
sudo mv /tmp/AppleColorEmoji.ttf /usr/local/share/fonts/apple-emoji/

# Oppdater font-cache
sudo fc-cache -fv

# Verifiser at fonten er installert
fc-list | grep -i apple
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
python scraper.py
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
git clone https://github.com/BePedersen/ryde-quicksight-dashboard.git
cd ryde-quicksight-dashboard

# Opprett .env og rediger CITY
cp .env.sample .env
nano .env  # Rediger CITY, THEME, DASHBOARD_MODE, etc.

# Installer Python-pakker
pip install -r requirements.txt

# Lag systemctl service
sudo bash -c 'cat > /etc/systemd/system/ryde-quicksight-dashboard.service << EOF
[Unit]
Description=AWS QuickSight Dashboard Display
After=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ryde-quicksight-dashboard
ExecStart=/usr/bin/python3 /home/pi/ryde-quicksight-dashboard/scraper.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
'

# Enable og start service
sudo systemctl daemon-reload
sudo systemctl enable ryde-quicksight-dashboard
sudo systemctl start ryde-quicksight-dashboard

# Sjekk at det kjører
sudo systemctl status ryde-quicksight-dashboard
```

### Vedlikehold via Pi Connect

**Endre konfigurasjon:**
```bash
# Rediger .env
nano /home/pi/ryde-quicksight-dashboard/.env

# Restart service
sudo systemctl restart ryde-quicksight-dashboard
```

**Sjekk status:**
```bash
# Se live logs
sudo journalctl -u ryde-quicksight-dashboard -f

# Sjekk service status
sudo systemctl status ryde-quicksight-dashboard
```

**Stopp/Start service:**
```bash
# Stopp
sudo systemctl stop ryde-quicksight-dashboard

# Start
sudo systemctl start ryde-quicksight-dashboard

# Restart
sudo systemctl restart ryde-quicksight-dashboard
```

### Oppdater kode fra GitHub

```bash
cd /home/pi/ryde-quicksight-dashboard
git pull
sudo systemctl restart ryde-quicksight-dashboard
```

### Kjør manuelt med screen (debugging)

For å kjøre scriptet manuelt i en persistent terminal-sesjon:

```bash
# Installer screen (første gang)
sudo apt install screen

# Start ny screen-sesjon
screen -S dashboard

# Kjør scriptet
cd /home/pi/ryde-quicksight-dashboard
python scraper.py

# Detach fra screen (scriptet fortsetter å kjøre)
# Trykk: Ctrl+A, deretter D

# List aktive screen-sesjoner
screen -ls

# Koble til eksisterende sesjon igjen
screen -r dashboard

# Avslutt screen-sesjon (når tilkoblet)
exit
```

## Støttede Byer

Tilgjengelige byvalg i `CITY`:
asker, bergen, bodø, borås, changzhou, drammen, eskilstuna, fredrikstad, göteborg, halmstad, helsingborg, hämeenlinna, helsinki, hq, joensuu, jyväskylä, karlstad, kristiansand, kuopio, lahti, lappeenranta, linköping, luleå, malmö, moss, norrköping, not used, oslo, oulu, östersund, örebro, pori, sandefjord, seinäjoki, shanghai, skien, stavanger, sundsvall, tampere, trondheim, tromsø, turku, umeå, uppsala, vaasa, västeräs, växjö

## Tema-bytte

- **Automatisk (standard):** Light mode 06:30-22:30, midnight mode 22:30-06:30
- **Manuell:** Sett `THEME=light` eller `THEME=midnight` i `.env` for å låse til ett tema

## Dashboard Health Check

Scriptet verifiserer automatisk at dashboardet er synlig og fungerer. Ved oppstart og etter hver refresh kjøres følgende sjekker:

| Sjekk | Beskrivelse |
|-------|-------------|
| `not_on_signin` | Ikke stuck på login-siden |
| `no_error_page` | Ingen feilmeldinger (Access denied, Something went wrong, etc.) |
| `dashboard_container` | Dashboard-container elementer finnes |
| `visuals_loaded` | Grafer, KPIs og tabeller er rendret |
| `no_loading_spinner` | Ingen loading-spinner synlig |

### Auto-restart

Hvis dashboardet ikke er synlig, restarter scriptet automatisk:

- **Ved oppstart:** Venter opptil 60 sekunder, restarter hvis dashboard ikke laster
- **Etter refresh:** Venter opptil 30 sekunder, restarter hvis dashboard forsvinner
- **Ved feil:** Restarter umiddelbart ved exceptions

Logs viser restart-årsak:
```
🔄 Restarter prosessen: Dashboard ikke synlig ved oppstart: No dashboard elements found
```

## Vedlikehold på flere Raspberry Pi-er

### Endre konfigurasjon via Pi Connect

Hver Pi administreres individuelt via Pi Connect:

1. **Åpne Pi Connect**
2. **Klikk på ønsket Pi-enhet**
3. **Velg "Remote shell"**
4. **Gjør endringer:**
   ```bash
   nano /home/pi/ryde-quicksight-dashboard/.env
   sudo systemctl restart ryde-quicksight-dashboard
   ```

### Batch oppdateringer

Hvis du trenger å oppdatere flere Pi-er samtidig, kan du:

```bash
# SSH inn på hver Pi (via Remote shell)
cd /home/pi/ryde-quicksight-dashboard
git pull
sudo systemctl restart ryde-quicksight-dashboard
```

## Feilsøking

### Ingen innlogging
- Sjekk `USERNAME` og `PASSWORD` i `.env`
- Sjekk at Chrome/Chromium er installert
- Se logs med: `sudo journalctl -u ryde-quicksight-dashboard -f`

### Feil tema eller by
- Sjekk at `CITY` og `THEME` er stavd riktig (små bokstaver)
- Restart service: `sudo systemctl restart ryde-quicksight-dashboard`

### Performance
- Øk `REFRESH_SECS` hvis Pi-en er treg
- Sjekk Chrome cache: `rm -rf /tmp/qschrome-profile` (fjerner lagret profil)

### Dashboard restarter i loop
Hvis scriptet restarter kontinuerlig:
- Sjekk at QuickSight-dashboardet faktisk eksisterer og er tilgjengelig
- Se logs for hvilken sjekk som feiler: `sudo journalctl -u ryde-quicksight-dashboard -f`
- Mulige årsaker: Nettverksproblemer, ugyldig dashboard-ID, session utløpt

## Lisens

MIT

## Kontakt

benjamin.pedersen@ryde-technology.com
