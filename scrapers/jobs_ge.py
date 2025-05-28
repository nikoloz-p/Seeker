def run_jobs_ge_script(log_callback=print) -> list[dict]:
    from selenium_config import get_driver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import time

    driver = get_driver()
    driver.get("https://jobs.ge/")
    time.sleep(3)

    for _ in range(40):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(0.3)

    rows = driver.find_elements(By.XPATH, '//table[@id="job_list_table"]//tr')[1:]
    data = []

    for row in rows:
        try:
            title_el = row.find_element(By.XPATH, './/td/a[contains(@class, "vip")]')
            tds = row.find_elements(By.XPATH, './/td')

            title = title_el.text.strip()
            title_url = title_el.get_attribute("href")

            company_text, company_url = "", ""
            for company in tds[2:]:
                text = company.text.strip()
                link = company.find_elements(By.TAG_NAME, 'a')
                if text:
                    company_text = text
                    if link:
                        company_url = link[0].get_attribute('href')
                    break

            published, end = tds[-2].text, tds[-1].text

            data.append({
                "position": title,
                "position_url": title_url,
                "company": company_text,
                "company_url": company_url,
                "published_date": published,
                "end_date": end,
                "date": time.strftime("%m-%d")
            })

            log_callback(f"Added {title} @ {company_text}")

            time.sleep(1)

        except Exception as e:
            log_callback(f"Error: {e}")

    driver.quit()
    log_callback(f"Scraping done. Total: {len(data)} jobs.")

    return data

run_jobs_ge_script()