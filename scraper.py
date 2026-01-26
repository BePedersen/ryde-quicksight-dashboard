#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium-basert QuickSight-visning i kiosk/fullskjerm.
- Logger inn (første gang), bruker persistent profil for senere oppstarter
- Håndterer "Show me more"-dialog
- Navigerer direkte til Operations-dashboardet
- Reloader hver 5. minutt uten ny innlogging
- Restarter prosessen daglig kl. 01:00

Krav:
- macOS: Google Chrome installert
- Raspberry Pi OS: chromium & chromedriver:  
  sudo apt install -y chromium chromium-driver
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Auto-oppsett av venv + pakker (selenium, python-dotenv)
VENV_PATH = Path.home() / "quicksight-env"
REQS = ["selenium", "python-dotenv"]

def ensure_env():
    try:
        if not (VENV_PATH / "bin" / "activate").exists():
            print(f"⚙️  Oppretter virtuelt miljø på {VENV_PATH} …")
            subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        pip = VENV_PATH / "bin" / "pip"
        for pkg in REQS:
            subprocess.run([str(pip), "install", "-q", pkg], check=True)
        if not sys.prefix.startswith(str(VENV_PATH)):
            py = VENV_PATH / "bin" / "python3"
            print(f"🔁 Restarter i miljø: {py}")
            os.execv(str(py), [str(py)] + sys.argv)
    except Exception as e:
        print("⚠️ Klarte ikke auto-oppsett av venv:", e)

ensure_env()

# Etter restart i venv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    load_dotenv = None

# ---------- KONFIG ----------
DEFAULT_URL = (
    "https://eu-central-1.quicksight.aws.amazon.com/sn/auth/signin"
    "?redirect_uri=https%3A%2F%2Feu-central-1.quicksight.aws.amazon.com%2Fsn%2Fauth%2Fsignin%2C%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue"
)
# Dashboard URL-er og sheet IDs
MIDNIGHT_DASHBOARD_ID = "4c86565f-7e0b-4b6b-bfea-14ca7f307bf7"
LIGHT_DASHBOARD_ID = "094b6397-67e5-4011-ad16-25e93041060d"

OPERATIONS_SHEET_ID_MIDNIGHT = "b3763094-7789-45e2-809f-293306b55f00"
MECHANICS_SHEET_ID_MIDNIGHT = "7913f79f-6d23-4328-9a63-4f8ad50bca36"
OPERATIONS_SHEET_ID_LIGHT = "b3db0892-09d5-4dcf-8490-e155e0360f16"
MECHANICS_SHEET_ID_LIGHT = "b8858404-f110-4efd-96f9-bf50ccf495be"

# City-mappinger
CITY_MAPPING = {
    "asker": "asker%20%26%20bærum",
    "bergen": "bergen",
    "bodø": "bodø",
    "borås": "borås",
    "changzhou": "changzhou%20%26%20shanghai",
    "drammen": "drammen",
    "eskilstuna": "eskilstuna",
    "fredrikstad": "fredrikstad%20%26%20sarpsborg",
    "göteborg": "göteborg",
    "halmstad": "halmstad",
    "helsingborg": "helsingborg",
    "hämeenlinna": "hämeenlinna",
    "helsinki": "helsinki%20%26%20espoo%20%26%20vantaa%20%26%20myyrmäki",
    "hq": "hq",
    "joensuu": "joensuu",
    "jyväskylä": "jyväskylä",
    "karlstad": "karlstad",
    "kristiansand": "kristiansand",
    "kuopio": "kuopio",
    "lahti": "lahti",
    "lappeenranta": "lappeenranta",
    "linköping": "linköping",
    "luleå": "luleå",
    "malmö": "malmö%20%26%20lund",
    "moss": "moss",
    "norrköping": "norrköping",
    "not used": "not used",
    "oslo": "oslo%20%26%20l%C3%B8renskog",
    "oulu": "oulu",
    "östersund": "östersund",
    "örebro": "örebro",
    "pori": "pori",
    "sandefjord": "sandefjord%20%26%20tønsberg",
    "seinäjoki": "seinäjoki",
    "shanghai": "shanghai",
    "skien": "skien%20%26%20porsgrunn",
    "stavanger": "stavanger%20%26%20sandnes%20%26%20sola",
    "sundsvall": "sundsvall",
    "tampere": "tampere",
    "trondheim": "trondheim",
    "tromsø": "tromsø",
    "turku": "turku%20%26%20raisio",
    "umeå": "umeå",
    "uppsala": "uppsala",
    "vaasa": "vaasa",
    "västeräs": "västeräs",
    "växjö": "växjö",
}

USER_PROFILE = os.getenv("QS_USER_PROFILE", "/tmp/qschrome-profile")
REFRESH_SECS = int(os.getenv("REFRESH_SECS", "300"))
HEADLESS = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes", "on")
DASHBOARD_MODE = os.getenv("DASHBOARD_MODE", "operations").lower()
CITY = os.getenv("CITY", "bergen").lower()

# Selectors
SEL_ACCOUNT = "#account-name-input"
SEL_EMAIL = "#username-input, input#username, input[name='username'], input[type='email']"
SEL_PASS = "input#awsui-input-0, input[id^='awsui-input'], input[type='password'], input.awsui-input-type-password, #password"
SEL_NEXT = "//button[contains(., 'Next') or contains(., 'Neste') or @type='submit']"
SEL_SIGNIN = "//button[contains(., 'Sign in') or @type='submit']"
SEL_SHOW_MORE = "//button[contains(., 'Show me more')]"


def getenv_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    return default if v is None else v.lower() in ("1", "true", "yes", "y", "on")


def get_current_theme():
    """
    Returner tema basert på .env THEME (hvis satt), ellers tidsbasert tema.
    - Hvis THEME er satt i .env: bruk den alltid
    - Hvis THEME ikke er satt: 'light' hvis tiden er mellom 06:30 og 22:30, ellers 'midnight'
    """
    theme_env = os.getenv("THEME", "").lower().strip()
    if theme_env in ("light", "midnight"):
        return theme_env

    # Hvis ikke satt eller ugyldig, bruk tidsbasert tema
    now = datetime.now().time()
    light_start = datetime.strptime("06:30", "%H:%M").time()
    light_end = datetime.strptime("22:30", "%H:%M").time()

    if light_start <= now < light_end:
        return "light"
    else:
        return "midnight"


def restart_process(driver=None, reason="Unknown"):
    """Restarter prosessen. Lukker driver først hvis gitt."""
    print(f"\n🔄 Restarter prosessen: {reason}")
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
    time.sleep(2)  # Kort pause før restart
    os.execv(sys.executable, [sys.executable] + sys.argv)


def next_restart_at(times=("06:00", "22:00")):
    """
    Returner neste restart-tidspunkt i dag/ i morgen gitt faste klokkeslett (lokal tid).
    times: tuple/list av klokkeslett på format HH:MM
    """
    now = datetime.now()
    candidates = []
    for t in times:
        hh, mm = map(int, t.split(":"))
        cand = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if cand <= now:
            cand += timedelta(days=1)
        candidates.append(cand)
    return min(candidates)


def split_candidates(csl: str):
    return [s.strip() for s in csl.split(",") if s.strip()]


def wait_any_css(driver, css_list: str, timeout=15):
    wait = WebDriverWait(driver, timeout)
    last_exc = None
    for css in split_candidates(css_list):
        try:
            el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
            return el
        except Exception as e:
            last_exc = e
    raise last_exc or TimeoutException(f"Ingen av CSS-selektorene ble funnet innen {timeout}s: {css_list}")


def click_xpath_if_present(driver, xpath: str, timeout=5):
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        el.click()
        return True
    except Exception:
        return False


def type_into(driver, css_list: str, text: str, timeout=15):
    el = wait_any_css(driver, css_list, timeout=timeout)
    try:
        el.clear()
    except Exception:
        pass
    el.send_keys(text)
    return True


def setup_driver():
    if load_dotenv:
        load_dotenv()

    account = os.getenv("ACCOUNT_NAME", "ryde-tech").strip()
    username = os.getenv("USERNAME", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    # Slett Chrome profil ved oppstart for å fjerne cache
    try:
        if os.path.exists(USER_PROFILE):
            shutil.rmtree(USER_PROFILE)
            print(f"🧹 Slettet Chrome profil cache: {USER_PROFILE}")
    except Exception as e:
        print(f"⚠️  Klarte ikke slette Chrome profil: {e}")

    # Opprett Default profil med deaktiverte password-innstillinger
    try:
        import json
        profile_path = Path(USER_PROFILE) / "Default"
        profile_path.mkdir(parents=True, exist_ok=True)

        prefs = {
            "profile": {
                "password_manager_enabled": False,
                "password_bubble_on_signin": False
            },
            "credentials_enable_service": False,
            "passwords": {},
            "autofill": {
                "enabled": False
            }
        }

        prefs_file = profile_path / "Preferences"
        with open(prefs_file, 'w') as f:
            json.dump(prefs, f)
        print(f"✅ Opprettet Chrome Preferences med deaktivert password manager")
    except Exception as e:
        print(f"⚠️  Klarte ikke opprette Chrome Preferences: {e}")

    # Finn Chrome/Chromium
    chrome_exec = (
        shutil.which("google-chrome") or
        shutil.which("google-chrome-stable") or
        shutil.which("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome") or
        shutil.which("chromium") or
        shutil.which("chromium-browser")
    )
    if not chrome_exec:
        print("❌ Fant ikke Chrome/Chromium. Installer Google Chrome (mac) eller chromium (Pi).")
        sys.exit(2)

    # Finn/bruk chromedriver
    driver_path = shutil.which("chromedriver")
    service = ChromeService(executable_path=driver_path) if driver_path else ChromeService()

    opts = ChromeOptions()
    opts.binary_location = chrome_exec
    opts.add_argument(f"--user-data-dir={USER_PROFILE}")
    opts.add_argument("--window-position=0,0")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-infobars")
    # Fjern "Chrome kontrolleres av programvare for automatisk testing"
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-session-crashed-bubble")
    opts.add_argument("--overscroll-history-navigation=0")
    opts.add_argument("--hide-scrollbars")
    # Fullskjerm/kiosk
    opts.add_argument("--start-maximized")
    opts.add_argument("--start-fullscreen")
    opts.add_argument("--kiosk")
    # Stabilitet for Raspberry Pi 4/5
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--no-zygote")
    opts.add_argument("--single-process")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-client-side-phishing-detection")
    opts.add_argument("--disable-component-update")
    opts.add_argument("--disable-sync")
    opts.add_argument("--no-first-run")
    opts.add_argument("--disable-breakpad")
    opts.add_argument("--disable-hang-monitor")
    opts.add_argument("--disable-ipc-flooding-protection")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--disable-password-generation")
    opts.add_argument("--disable-autofill")
    opts.add_argument("--disable-credentials-api")
    opts.add_argument("--disable-offer-store-unmasked-passwords")
    opts.add_argument("--disable-password-manager")
    opts.add_argument("--disable-password-manager-ui")
    opts.add_argument("--disable-password-manager-ui-for-signin")
    opts.add_argument("--disable-fillonaccount-select")
    opts.add_argument("--disable-ipcflooding-protection")
    opts.add_argument("--noerrdialogs")
    opts.add_argument("--disable-low-res-tiling")
    opts.add_argument("--disable-zero-copy")
    opts.add_argument("--enable-features=UseOzonePlatform")
    opts.add_argument("--ozone-platform=wayland")

    if HEADLESS:
        opts.add_argument("--headless=new")

    driver = webdriver.Chrome(service=service, options=opts)
    try:
        driver.fullscreen_window()  # ekstra sikkerhet
    except Exception:
        pass

    return driver, account, username, password


def login_if_needed(driver, account, username, password, target_url=DEFAULT_URL):
    print("➡️  Går til innloggingssiden …")
    driver.get(target_url)
    time.sleep(1.0)

    # Hvis vi allerede er innlogget (pga persistent profil), gå direkte til dashboard
    if "signin" not in driver.current_url.lower():
        print("✅ Allerede innlogget (profil). Hopper til dashboard …")
        return True

    # 1) Account name
    try:
        print("🔎 Fyller konto-navn …")
        type_into(driver, SEL_ACCOUNT, account, timeout=15)
        if not click_xpath_if_present(driver, SEL_NEXT, timeout=5):
            print("ℹ️  Fant ikke Next-knapp etter konto. Fortsetter …")
    except Exception as e:
        print("ℹ️  Konto-felt ikke synlig:", e)

    # 2) E-post / brukernavn
    try:
        print("📧 Fyller e-post …")
        type_into(driver, SEL_EMAIL, username, timeout=15)
        if not click_xpath_if_present(driver, SEL_NEXT, timeout=5):
            print("ℹ️  Fant ikke Next-knapp etter e-post. Fortsetter …")
    except Exception as e:
        print("❌ Fant ikke e-postfelt:", e)

    # 3) Passord
    try:
        print("🔐 Fyller passord …")
        type_into(driver, SEL_PASS, password, timeout=15)
    except Exception as e:
        print("❌ Fant ikke passordfelt:", e)

    # 4) Sign in
    if not click_xpath_if_present(driver, SEL_SIGNIN, timeout=10):
        print("ℹ️  Fant ikke 'Sign in'-knapp – forsøker å submitte med Enter …")
        try:
            el = wait_any_css(driver, SEL_PASS, timeout=5)
            el.submit()
        except Exception:
            pass

    # Vent på at vi forlater signin
    try:
        WebDriverWait(driver, 60).until(lambda d: "signin" not in d.current_url.lower())
        print("✅ Innlogging OK.")
        return True
    except TimeoutException:
        print("⚠️  Ser fortsatt signin-URL – kanskje MFA eller feil passord?")
        return False


def check_dashboard_visible(driver, timeout=30):
    """
    Sjekker om QuickSight-dashboardet er synlig og lastet korrekt.

    Returnerer:
        dict med status:
        - 'visible': True hvis dashboardet er synlig
        - 'reason': Beskrivelse av status
        - 'checks': Dict med individuelle sjekker
    """
    checks = {
        'not_on_signin': False,
        'no_error_page': False,
        'dashboard_container': False,
        'visuals_loaded': False,
        'no_loading_spinner': False,
    }

    try:
        current_url = driver.current_url.lower()

        # 1. Sjekk at vi ikke er på innloggingssiden
        checks['not_on_signin'] = 'signin' not in current_url
        if not checks['not_on_signin']:
            return {
                'visible': False,
                'reason': 'Stuck on signin page',
                'checks': checks
            }

        # 2. Sjekk for feilsider
        error_indicators = [
            "//div[contains(@class, 'error')]//h1",
            "//div[contains(text(), 'Something went wrong')]",
            "//div[contains(text(), 'Access denied')]",
            "//div[contains(text(), 'not found')]",
        ]
        has_error = False
        for xpath in error_indicators:
            try:
                el = driver.find_element(By.XPATH, xpath)
                if el.is_displayed():
                    has_error = True
                    break
            except NoSuchElementException:
                pass
        checks['no_error_page'] = not has_error
        if not checks['no_error_page']:
            return {
                'visible': False,
                'reason': 'Error page detected',
                'checks': checks
            }

        # 3. Sjekk at dashboard-container finnes
        dashboard_selectors = [
            "[class*='dashboard']",
            "[class*='Dashboard']",
            "[data-testid='dashboard']",
            ".quicksight-embedding-iframe",
            "[class*='visual-container']",
            "[class*='sheet-container']",
        ]
        for selector in dashboard_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                if el.is_displayed():
                    checks['dashboard_container'] = True
                    break
            except NoSuchElementException:
                pass

        # 4. Sjekk at visuals (grafer, tabeller) er lastet
        visual_selectors = [
            "[class*='visual']",
            "[class*='chart']",
            "[class*='kpi']",
            "[class*='table']",
            "svg[class*='chart']",
            "canvas",
            "[class*='insight']",
        ]
        visuals_found = 0
        for selector in visual_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                visuals_found += sum(1 for el in elements if el.is_displayed())
            except Exception:
                pass
        checks['visuals_loaded'] = visuals_found >= 1

        # 5. Sjekk at det ikke er loading spinner synlig
        spinner_selectors = [
            "[class*='loading']",
            "[class*='spinner']",
            "[class*='Loading']",
            "[class*='Spinner']",
            "[role='progressbar']",
        ]
        spinner_visible = False
        for selector in spinner_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed():
                        # Dobbeltsjekk at det faktisk er en spinner (ikke bare et element med loading i navnet)
                        size = el.size
                        if size['width'] > 0 and size['height'] > 0:
                            spinner_visible = True
                            break
            except Exception:
                pass
            if spinner_visible:
                break
        checks['no_loading_spinner'] = not spinner_visible

        # Evaluer samlet status
        # Dashboard er synlig hvis vi har container ELLER visuals, og ingen spinner
        is_visible = (
            checks['not_on_signin'] and
            checks['no_error_page'] and
            (checks['dashboard_container'] or checks['visuals_loaded']) and
            checks['no_loading_spinner']
        )

        if is_visible:
            reason = f"Dashboard visible ({visuals_found} visuals found)"
        elif not checks['no_loading_spinner']:
            reason = "Dashboard still loading"
        elif not checks['dashboard_container'] and not checks['visuals_loaded']:
            reason = "No dashboard elements found"
        else:
            reason = "Dashboard state unclear"

        return {
            'visible': is_visible,
            'reason': reason,
            'checks': checks
        }

    except Exception as e:
        return {
            'visible': False,
            'reason': f"Check failed: {e}",
            'checks': checks
        }


def wait_for_dashboard_visible(driver, timeout=60, poll_interval=2):
    """
    Venter til dashboardet er synlig, med timeout.

    Args:
        driver: Selenium WebDriver
        timeout: Maks ventetid i sekunder
        poll_interval: Hvor ofte vi sjekker (sekunder)

    Returns:
        dict med status fra check_dashboard_visible, eller timeout-feil
    """
    start_time = time.time()
    last_status = None

    while (time.time() - start_time) < timeout:
        status = check_dashboard_visible(driver)
        last_status = status

        if status['visible']:
            elapsed = time.time() - start_time
            print(f"✅ Dashboard synlig etter {elapsed:.1f}s: {status['reason']}")
            return status

        time.sleep(poll_interval)

    elapsed = time.time() - start_time
    print(f"⚠️  Timeout etter {elapsed:.1f}s: {last_status['reason'] if last_status else 'Unknown'}")
    return last_status or {
        'visible': False,
        'reason': f'Timeout after {timeout}s',
        'checks': {}
    }


def close_password_dialog(driver):
    """Lukk password dialogen ved å klikke 'Aldri' eller 'Never' knapp"""
    try:
        driver.execute_script("""
            // Søk etter alle knapper og finn den som sier "aldri" eller "never"
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.textContent.trim();
                if (text.toLowerCase().includes('aldri') ||
                    text.toLowerCase().includes('never')) {
                    console.log('Fant knapp: ' + text);
                    btn.click();
                    return true;
                }
            }
            return false;
        """)
    except Exception:
        pass


def close_show_me_more(driver):
    # Håndter "Show me more" hvis den finnes
    try:
        if click_xpath_if_present(driver, SEL_SHOW_MORE, timeout=6):
            print("✅ Lukket 'Show me more'.")
            time.sleep(1.0)
    except Exception:
        pass


def keep_open_and_reload(driver, operations_url):
    print("🖥️ Dashboardet er åpent. Holder visning i gang.")
    print("🔄 Reloader hver 5. minutt uten ny innlogging.")
    print("⏰ Restarter prosessen automatisk hver dag kl. 06:30, 14:30 og 22:30.")

    last_reload = datetime.now()
    restart_at = next_restart_at(("06:30", "14:30", "22:30"))

    try:
        while True:
            now = datetime.now()
            if now >= restart_at:
                restart_process(driver, f"Daglig planlagt restart kl. {now:%H:%M}")

            elapsed = (now - last_reload).total_seconds()
            if elapsed >= REFRESH_SECS:
                try:
                    print(f"🔄 Refresh (etter {elapsed:.0f}s) …")
                    # Gentle refresh med JavaScript F5 istedenfor driver.get()
                    driver.execute_script("location.reload();")
                    print("  ✓ location.reload() kjørt")
                    time.sleep(3.0)
                    close_password_dialog(driver)
                    close_show_me_more(driver)
                    print("  ✓ dialoger lukket")

                    # Verifiser at dashboardet er synlig etter refresh
                    status = wait_for_dashboard_visible(driver, timeout=30, poll_interval=2)
                    if not status['visible']:
                        print(f"⚠️  Dashboard ikke synlig etter refresh: {status['reason']}")
                        print(f"    Checks: {status['checks']}")
                        restart_process(driver, f"Dashboard ikke synlig: {status['reason']}")

                    last_reload = datetime.now()
                    print("✅ Refresh ferdig.")
                except Exception as e:
                    print("⚠️  Feil under refresh:", e)
                    import traceback
                    traceback.print_exc()
                    restart_process(driver, f"Feil under refresh: {e}")

            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\n⛔ Avslutter på brukerkommando …")
        try:
            driver.quit()
        except Exception:
            pass


def main():
    account = os.getenv("ACCOUNT_NAME", "ryde-tech").strip()
    username = os.getenv("USERNAME", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    # Bygg dashboard URL basert på tema (tidsbasert), modus og by
    theme = get_current_theme()
    dashboard_id = LIGHT_DASHBOARD_ID if theme == "light" else MIDNIGHT_DASHBOARD_ID

    if DASHBOARD_MODE == "mechanics":
        sheet_id = MECHANICS_SHEET_ID_LIGHT if theme == "light" else MECHANICS_SHEET_ID_MIDNIGHT
    else:
        sheet_id = OPERATIONS_SHEET_ID_LIGHT if theme == "light" else OPERATIONS_SHEET_ID_MIDNIGHT

    city_param = CITY_MAPPING.get(CITY, "")
    city_query = f"#p.City={city_param}" if city_param else ""

    operations_url = f"https://eu-central-1.quicksight.aws.amazon.com/sn/account/ryde-tech/dashboards/{dashboard_id}/sheets/{dashboard_id}_{sheet_id}{city_query}"

    print("🚀 Starter Selenium-visning …")
    print(f"📊 Konfig: {theme.upper()} | {DASHBOARD_MODE.upper()} | {CITY.upper()}")
    driver, account, username, password = setup_driver()

    ok = True
    if not username or not password:
        print("ℹ️  USERNAME/PASSWORD mangler – forsøker å bruke lagret profil direkte …")
    else:
        ok = login_if_needed(driver, account, username, password, DEFAULT_URL)

    # Hvis allerede innlogget, eller login gikk bra:
    print("🌐 Åpner dashboardet …")
    driver.get(operations_url)
    # Aggressivt lukk password dialogs mens siden laster
    for i in range(5):
        time.sleep(0.5)
        close_password_dialog(driver)
    close_show_me_more(driver)

    # Skriv ut litt status
    # (Vi venter ikke på spesifikk by i tittel siden den varierer basert på CITY)
    try:
        print("📄 Tittel:", driver.title)
        print("🔗 URL:", driver.current_url)
    except Exception:
        pass

    # Verifiser at dashboardet er synlig før vi starter refresh-loopen
    print("🔍 Verifiserer at dashboardet er synlig …")
    status = wait_for_dashboard_visible(driver, timeout=60, poll_interval=3)
    if status['visible']:
        print(f"✅ Dashboard bekreftet synlig: {status['reason']}")
    else:
        print(f"⚠️  Dashboard ikke synlig: {status['reason']}")
        print(f"    Checks: {status['checks']}")
        restart_process(driver, f"Dashboard ikke synlig ved oppstart: {status['reason']}")

    keep_open_and_reload(driver, operations_url)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("❌ Avsluttet med feil:", exc)
        sys.exit(1)