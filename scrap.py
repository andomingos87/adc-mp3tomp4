from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

def fetch_iframe_src(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        iframe_src = iframe.get_attribute('src')

        if iframe_src:
            parsed_url = urlparse(iframe_src)
            return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        else:
            return None
    finally:
        driver.quit()
