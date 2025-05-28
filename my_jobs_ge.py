from selenium_config import get_driver
from selenium.webdriver.common.by import By
import time
import json

driver = get_driver()
driver.get('https://myjobs.ge/ka/vacancy?page=1')

time.sleep(3)


pagination = driver.find_elements(By.XPATH, '//ul[@class="react-paginate mt-8"]/li[not(@class)]/a')
last_page = pagination[-1].text

data = []

for page in range(1, int(last_page)+1):
    driver.get(f'https://myjobs.ge/ka/vacancy?page={page}')
    time.sleep(3)

    containers = driver.find_elements(By.XPATH, '//div[@class="flex justify-between border-neutral-40 w-full"]')

    for i in range(len(containers)):
        try:
            container = containers[i]
            
            company = container.find_element(By.XPATH, './/div[@class="flex gap-2 pb-1"]/p').text
            position = container.find_element(By.TAG_NAME, 'h5').text
            date = container.find_element(By.XPATH, './/div[@class="absolute inset-0 flex items-center justify-end"]/span').text
            
            current_tab = driver.current_window_handle
            
            container.click()
            
            new_tab = [h for h in driver.window_handles if h != current_tab][0]
            driver.switch_to.window(new_tab)
            position_url = driver.current_url
            print("Clicked:", position_url)
            driver.close()
            
            driver.switch_to.window(current_tab)
            
            data.append({
                "position": position,
                "company": company,
                "date": date,
                'position_url': position_url,
            })
            
            print(f"added {company}: {position}")
            
        except Exception as e:
            print(e)
    
    
with open("my_jobs_ge.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    
driver.quit()