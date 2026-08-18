import logging
import random
import tempfile
import time
import zipfile
import json

from icecream import ic
from pathlib import Path

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from tbselenium.tbdriver import TorBrowserDriver

porno = 'https://www.xvideos.com/video.kvdeipdea52/one_of_the_most_bizarre_pornos_in_the_world'
nf = 'https://www.noweformy.org/'
ss_path = '/home/kobi/pykam_popcorn/'
timeout = 120

def pause():
    time.sleep(random.uniform(2, 5))

def install_referer_spoofer(driver):
    referer = porno
    target_pattern = nf.rstrip("/") + "/*"

    tmpdir = Path(tempfile.mkdtemp())
    xpi_path = tmpdir / "referer_spoofer.xpi"

    manifest = {
        "manifest_version": 2,
        "name": "Temporary Referer Spoofer",
        "version": "1.0",
        "permissions": [
            "webRequest",
            "webRequestBlocking",
            target_pattern
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }

    background_js = f"""
    function changeReferer(details) {{
        let headers = details.requestHeaders.filter(
            h => h.name.toLowerCase() !== "referer"
        );

        headers.push({{
            name: "Referer",
            value: {json.dumps(referer)}
        }});

        return {{ requestHeaders: headers }};
    }}

    browser.webRequest.onBeforeSendHeaders.addListener(
        changeReferer,
        {{ urls: [{json.dumps(target_pattern)}] }},
        ["blocking", "requestHeaders"]
    );
    """

    with zipfile.ZipFile(xpi_path, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("background.js", background_js)

    addon_id = driver.install_addon(
        str(xpi_path),
        temporary=True
    )

    return addon_id

def unspoof_referer(driver, addon_id):
    driver.uninstall_addon(addon_id)

def random_link(driver):
    links = []

    for link in driver.find_elements(By.TAG_NAME, "a"):
        href = link.get_attribute("href")

        if (
                link.is_displayed()
                and link.is_enabled()
                and href
                and href.startswith(("http://", "https://"))
        ):
            links.append(link)

    if links:
        driver.set_page_load_timeout(timeout)
        try:
            random.choice(links).click()
        except TimeoutException:
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass

def hardened_get(driver, url):
    driver.set_page_load_timeout(timeout)
    try:
        driver.get(url)
    except TimeoutException:
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

options = Options()
options.set_preference(
    "general.useragent.override",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0"
)
options.add_argument("--width=1920")
options.add_argument("--height=1080")

while True:
    with TorBrowserDriver("/home/kobi/tor-browser", headless=True, options=options,
    tbb_logfile_path="/tmp/geckodriver.log") as driver:
        pause()
        addon = install_referer_spoofer(driver)
        hardened_get(driver, nf)
        driver.save_screenshot(ss_path + "last_screenshot_1.png")
        ic('screenshot 1 saved.')
        unspoof_referer(driver, addon)
        pause()
        random_link(driver)
        pause()
        driver.save_screenshot(ss_path + "last_screenshot_2.png")
        ic('screenshot 2 saved.')
        hardened_get(driver, porno)
        pause()
