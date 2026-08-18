import random
import time

from tbselenium.tbdriver import TorBrowserDriver

porno = 'https://www.xvideos.com/video.kvdeipdea52/one_of_the_most_bizarre_pornos_in_the_world'
nf = 'https://www.noweformy.org/'

def pause():
    time.sleep(random.uniform(2, 5))

def spoof_referer(driver):
    driver.execute_script("""
    window.changeReferer = function(details) {
        let headers = details.requestHeaders.filter(
            h => h.name.toLowerCase() !== "referer"
        );

        headers.push({
            name: "Referer",
            value: "\"""" + porno + """\""
        });

        return {requestHeaders: headers};
    };

    browser.webRequest.onBeforeSendHeaders.addListener(
        window.changeReferer,
        {urls: [\"""" + nf + """\"/*"]},
        ["blocking", "requestHeaders"]
    );
    """)

def unspoof_referer(driver):
    driver.execute_script("""
    browser.webRequest.onBeforeSendHeaders.removeListener(
        window.changeReferer
    );
    """)

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
        random.choice(links).click()

while True:
    with TorBrowserDriver("/home/kobi/tor-browser", headless=True) as driver:
        pause()
        spoof_referer(driver)
        driver.get(nf)
        unspoof_referer(driver)
        pause()
        random_link(driver)
        pause()
        driver.save_screenshot("last_screenshot.png")
        driver.get(porno)
        pause()
