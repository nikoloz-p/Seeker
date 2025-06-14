from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

def get_driver(user_agent=None, headless=True):
    if user_agent is None:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_agent}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(base_dir, "..", "chromedriver.exe")
    driver_path = os.path.abspath(driver_path)

    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })
    
    return driver
