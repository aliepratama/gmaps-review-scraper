import json
import time
from .driver import init_driver
from .parser import scroll_reviews, parse_reviews
from .config import Settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_reviews(cfg: Settings) -> None:
    driver = init_driver(cfg.headless)
    try:
        driver.get(cfg.place_url)
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Try multiple selectors for the reviews button
        review_button_selectors = [
            "//button[contains(@aria-label,'ulasan')]",
            "//button[contains(@aria-label,'Ulasan')]",
            "//button[contains(@aria-label,'reviews')]",
            "//button[contains(@aria-label,'review')]",
            "//button[contains(text(),'reviews')]",
            "//button[contains(text(),'Ulasan')]",
            "//div[contains(@role,'button')][contains(@aria-label,'reviews')]"
        ]
        
        # Try each selector
        clicked = False
        for selector in review_button_selectors:
            try:
                # Wait explicitly for the element to be clickable
                review_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                review_button.click()
                clicked = True
                print(f"Successfully clicked review button with selector: {selector}")
                break
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not clicked:
            raise Exception("Could not find or click the reviews button")
        
        # Wait a bit for reviews to load after clicking
        time.sleep(2)
        
        scroll_reviews(driver, getattr(cfg, 'scroll_pause', 1), getattr(cfg, 'max_scrolls', 20))
        data = parse_reviews(driver, cfg.star_filter)
    finally:
        driver.quit()

    with open(cfg.output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] {len(data)} review disimpan di {cfg.output_path}")
