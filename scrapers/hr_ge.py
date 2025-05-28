def run_hr_ge_script(log_callback=print) -> list[dict]:
    from selenium_config import get_driver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import datetime
    import time

    driver = get_driver()
    driver.get('https://www.hr.ge/search-posting')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="paging-container"]//a[contains(@class, "item")]'))
    )

    pages = driver.find_elements(By.XPATH, '//div[@class="paging-container"]//a[contains(@class, "item")]')
    last_page = int(pages[-1].text)

    data = []

    for page in range(1, last_page + 1):
        time.sleep(5)

        log_callback(f"Scraping page {page}/{last_page}")
        driver.get(f'https://www.hr.ge/search-posting?pg={page}')

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "container--without-large-size")]'))
        )

        container = driver.find_elements(By.XPATH, '//div[contains(@class, "container--without-large-size")]')

        for job in container:
            try:
                position = job.find_element(By.XPATH, './/a[contains(@class, "title-link")]')
                position_title = position.text
                position_url = position.get_attribute('href')
                company = job.find_element(By.XPATH, './/div[contains(@class, "company")]/a/div').text
                company_url = job.find_element(By.XPATH, './/div[contains(@class, "company")]/a').get_attribute('href')
                dates = job.find_elements(By.XPATH, './/div[@class="date"]/span')

                published_date = ""
                end_date = ""

                if len(dates) >= 2:
                    published_date_text = dates[0].text.strip().replace('-', '')
                    end_date_text = dates[-1].text.strip()

                    published_date = (
                        datetime.date.today().strftime("%m-%d")
                        if published_date_text == "დღეს"
                        else published_date_text
                    )

                    end_date = (
                        datetime.date.today().strftime("%m-%d")
                        if end_date_text == "დღეს"
                        else end_date_text
                    )

                data.append({
                    'position': position_title,
                    'position_url': position_url,
                    'company': company,
                    'company_url': company_url,
                    'published_date': published_date,
                    'end_date': end_date,
                })

                log_callback(f"Added {position_title} @ {company}")

            except Exception as e:
                log_callback(e)

    driver.quit()
    log_callback(f"Scraping done. Total: {len(data)} jobs.")

    return data


run_hr_ge_script()