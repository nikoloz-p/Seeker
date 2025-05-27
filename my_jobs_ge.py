from selenium_config import get_driver
from selenium.webdriver.common.by import By
import time
import json

driver = get_driver()
driver.get('https://myjobs.ge/vacancy')

time.sleep(3)


pagination = driver.find_elements(By.XPATH, '//ul[@class="react-paginate mt-8"]/li[not(@class)]/a')
last_page = pagination[-1].text

data = []

for page in range(1, 3): #int(last_page)+1
    driver.get(f'https://myjobs.ge/ka/vacancy?page={page}')
    time.sleep(3)

    containers = driver.find_elements(By.XPATH, '//div[@class="flex justify-between border-neutral-40 w-full"]')

    for container in containers:
        try:
            company = container.find_element(By.XPATH, './/div[@class="flex gap-2 pb-1"]/p').text
            position = container.find_element(By.TAG_NAME, 'h5').text
            date = container.find_element(By.XPATH, './/div[@class="absolute inset-0 flex items-center justify-end"]/span').text
            
            data.append({
                "position": position,
                "company": company,
                "date": date
            })
            
            print(f"added {company}: {position}")
            
        except Exception as e:
            print(e)
    
    
with open("my_jobs_ge.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    
driver.quit()