import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

def scroll_reviews(driver: WebDriver, pause: float, max_iters: int) -> None:
    panel = driver.find_element(By.CSS_SELECTOR, 'div[role="region"]')
    for _ in range(max_iters):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
        time.sleep(pause)

def parse_reviews(driver: WebDriver, star_filter: list[int] | None = None) -> list[dict]:
    cards = driver.find_elements(By.CSS_SELECTOR, 'div[jscontroller="H6eOGe"]')
    result = []
    desired = set(star_filter) if star_filter else None

    for c in cards:
        try:
            author = c.find_element(By.CSS_SELECTOR, 'div.d4r55').text
            date   = c.find_element(By.CSS_SELECTOR, 'span.dehysf').text
            stars_text = c.find_element(By.CSS_SELECTOR, 'span.ODSEW-ShBeI-stars')\
                            .get_attribute('aria-label')
            stars  = int(float(stars_text.split()[0]))
            text   = c.find_element(By.CSS_SELECTOR, 'span.raw__09lO3').text

            if (desired is None) or (stars in desired):
                result.append({
                    "author": author,
                    "date":   date,
                    "stars":  stars,
                    "text":   text
                })
        except Exception:
            continue
    return result
