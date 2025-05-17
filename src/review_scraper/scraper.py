import json
from .driver import init_driver
from .parser import scroll_reviews, parse_reviews
from .config import Settings

def scrape_reviews(cfg: Settings) -> None:
    driver = init_driver(cfg.headless)
    try:
        driver.get(cfg.place_url)
        driver.implicitly_wait(5)
        driver.find_element_by_xpath("//button[contains(@aria-label,'ulasan')]").click()
        scroll_reviews(driver, cfg.scroll_pause, cfg.max_scrolls)
        data = parse_reviews(driver, cfg.star_filter)
    finally:
        driver.quit()

    with open(cfg.output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] {len(data)} review disimpan di {cfg.output_path}")
