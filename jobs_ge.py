from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json

# User agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Selenium settings

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--start-maximized")
options.add_argument(f"user-agent={user_agent}")

driver = webdriver.Chrome (service=Service(ChromeDriverManager().install()), options=options)


driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
})

driver.get("https://jobs.ge/")

# Scroll
for _ in range(40):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(0.3)

# Parse job list
rows = driver.find_elements(By.XPATH, '//table[@id="job_list_table"]//tr')[1:]


data = []

for row in rows:

    try:
        # Containers
        title_el = row.find_element(By.XPATH, './/td/a[contains(@class, "vip")]')
        tds = row.find_elements(By.XPATH, './/td')

        # Title
        title = title_el.text.strip()
        title_url = title_el.get_attribute("href")

        # Company
        company_text = ""
        company_url = ""

        for company in tds[2:]:
            text = company.text.strip()
            link = company.find_elements(By.TAG_NAME, 'a')

            if text:
                company_text = text
                if link:
                    company_url = link[0].get_attribute('href')
                break

        dates = []

        for date in tds[-2:]:
            dates.append(date.text)

        # Save data
        data.append({
            "position": title,
            "position_url": title_url,
            "company": company_text,
            'company_url': company_url,
            "published_date": dates[0],
            "end_date": dates[1],
        })
        print(f'added {title}:{company_text}')

    except Exception as e:
        print(e)

driver.quit()

with open("jobs_ge.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved to jobs_ge.json")