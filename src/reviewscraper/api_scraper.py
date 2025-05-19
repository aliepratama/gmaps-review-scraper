import base64
import brotli
import json
import time
from typing import List, Dict, Any, Optional
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from .config import Settings

def init_api_driver(headless: bool = True) -> webdriver.Chrome:
    """Initialize a Selenium Wire Chrome driver."""
    # Configure selenium-wire to capture more requests
    seleniumwire_options = {
        'disable_encoding': True,  # Don't decode encoded responses
        'enable_har': True,        # Enable HAR format
        'ignore_http_methods': ['OPTIONS'],  # Ignore OPTIONS requests
    }
    
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    
    # Create a service object with ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    
    # Pass service, options, and seleniumwire_options
    driver = webdriver.Chrome(
        service=service, 
        options=opts,
        seleniumwire_options=seleniumwire_options
    )
    
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    driver.set_window_size(1200, 800)
    
    # Use a broader scope to capture more requests
    driver.scopes = [
        r'.*maps\.google\.com.*',  # Added r prefix for raw string
        r'.*google\.com/maps.*'    # Added r prefix for raw string
    ]
    
    return driver

def extract_reviews_from_api(response_body: bytes) -> List[Dict[str, Any]]:
    """Extract review data from the API response."""
    try:
        # Save raw response for debugging
        with open("raw_response.bin", "wb") as f:
            f.write(response_body)
            
        # Decompress the brotli-compressed data
        try:
            decompressed = brotli.decompress(response_body)
            content = decompressed.decode('utf-8')
        except Exception as e:
            print(f"Decompression failed: {e}. Treating as raw content.")
            content = response_body.decode('utf-8', errors='replace')

        # Handle Google's response format which often starts with ")]}',"
        if content.startswith(")]}'"):
            content = content[4:]
        
        # Parse the JSON response
        data = json.loads(content)
        
        # For debugging, save the full response to inspect structure
        with open("api_response_debug.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Extract reviews
        reviews = []
        
        # Navigate through the nested structure to find reviews
        if isinstance(data, list) and len(data) > 2:
            review_blocks = data[2]
            
            if not isinstance(review_blocks, list):
                print("Expected review_blocks to be a list, but it's not.")
                return []
            
            for review_block in review_blocks:
                if not review_block or not isinstance(review_block, list) or len(review_block) < 1:
                    continue
                    
                # Extract basic review info
                try:
                    # Extract reviewer info
                    reviewer_info = {}
                    if len(review_block) > 0 and isinstance(review_block[0], list) and len(review_block[0]) > 5:
                        reviewer_data = review_block[0]
                        if reviewer_data and len(reviewer_data) > 2:
                            reviewer_info = {
                                "name": reviewer_data[1][4][5][0] if reviewer_data[0] else "Unknown",
                                "profile_url": reviewer_data[1][4][5][2][0] if len(reviewer_data) > 2 else None,
                                "profile_pic": reviewer_data[1][4][5][1] if len(reviewer_data) > 1 else None
                            }
                    
                    # Extract rating
                    rating = None
                    if len(review_block) > 0 and isinstance(review_block[0], list):
                        rating = review_block[0][2][0]
                    
                    # Extract review text
                    review_text = review_block[0][2][15][0][0] if len(review_block[0]) > 2 and review_block[0][2] else ""
                    
                    # Extract review date (usually in the first block)
                    review_date = None
                    if len(review_block) > 0 and isinstance(review_block[0], list) and len(review_block[0]) > 3:
                        review_date = review_block[0][1][3]
                    
                    review = {
                        "reviewer": reviewer_info,
                        "stars": rating,
                        "text": review_text,
                        "date": review_date,
                    }
                    
                    reviews.append(review)
                    
                except (IndexError, TypeError) as e:
                    print(f"Error extracting review data: {e}")
                    continue
                    
        return reviews
    except Exception as e:
        print(f"Error extracting reviews from API: {str(e)}")
        return []

def scrape_reviews_api(cfg: Settings) -> List[Dict[str, Any]]:
    """Scrape reviews using the Google Maps API directly."""
    driver = init_api_driver(cfg.headless)
    all_reviews = []
    
    try:
        # Navigate to the place page and wait for it to load
        driver.get(cfg.place_url)
        print("Waiting for page to load...")
        time.sleep(5)  # Give more time for initial page load
        
        # Clear request history
        driver.requests.clear()
        print("Cleared request history")
        
        # Click on the Ulasan/Reviews tab
        review_selectors = [
            "//button[contains(@aria-label,'Ulasan')]",
            "//button[contains(text(),'Ulasan')]",
            "//div[@role='tab'][contains(text(),'Ulasan')]",
            "//button[contains(text(),'Reviews')]", 
            "//div[@role='tab'][contains(text(),'Reviews')]",
            "//button[contains(@aria-label,'reviews')]",
            "//button[contains(@aria-label,'ulasan')]"
        ]
        
        clicked = False
        for selector in review_selectors:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"Found clickable element with selector: {selector}")
                element.click()
                clicked = True
                print("Clicked on reviews tab")
                break
            except Exception as e:
                print(f"Failed with selector {selector}: {str(e)}")
                continue
                
        if not clicked:
            print("Warning: Could not click on reviews tab")
        
        # Wait for reviews to load
        time.sleep(3)
        # Click the "Sort reviews" button
        try:
            sort_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Urutkan ulasan"]'))
            )
            print("Found sort reviews button, clicking it")
            sort_button.click()
            time.sleep(2)  # Wait for sort options to appear
            print("Clicked sort reviews button")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Could not find sort reviews button: {str(e)}")
            # Try alternative selectors
            try:
                alternative_selectors = [
                    'button[aria-label="Sort reviews"]',
                    'button.DVeyrd',
                    'button[jsaction*="pane.reviewSort"]'
                ]
                for selector in alternative_selectors:
                    try:
                        sort_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        print(f"Found sort button with alternative selector: {selector}")
                        sort_button.click()
                        time.sleep(2)
                        print("Clicked sort button with alternative selector")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"Failed to find any sort button: {str(e)}")

        # Click on the sort option based on the sort_direction
        # data-index="1" is oldest first (asc), data-index="3" is newest first (desc)
        sort_index = "3" if cfg.sort_direction == "asc" else "2"
        sort_label = "oldest" if cfg.sort_direction == "asc" else "newest"
        
        try:
            sort_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'div.fxNQSd[data-index="{sort_index}"]'))
            )
            print(f"Found '{sort_label}' sort option, clicking it")
            sort_option.click()
            time.sleep(2)  # Wait for sorting to take effect
            print(f"Clicked on '{sort_label}' sort option")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Could not find or click '{sort_label}' sort option: {str(e)}")
            # Try alternative selectors
            alternative_selectors = [
                f'div[data-value="{sort_label.upper()}"]',
                f'div[data-value="{sort_label}"]',
                f'li[aria-label="Sort by: {sort_label.capitalize()}"]',
                f'li[data-index="{sort_index}"]'
            ]
            for selector in alternative_selectors:
                try:
                    sort_option = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"Found sort option with alternative selector: {selector}")
                    sort_option.click()
                    time.sleep(2)
                    print(f"Clicked sort option using selector: {selector}")
                    break
                except Exception:
                    continue
        
        time.sleep(5)
        # Find the reviews container - try multiple selectors used by Google Maps
        container_selectors = [
            'div[role="region"]',
            'div.m6QErb-qJTHM-haAclf',
            'div.m6QErb[aria-label]',
            'div.m6QErb',
            'div.section-scrollbox'
        ]
        
        review_container = None
        for selector in container_selectors:
            try:
                review_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"Found review container with selector: {selector}")
                break
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not review_container:
            print("Warning: Could not find the review container. Falling back to global scrolling.")
        
        # Focus the scraper specifically on listugcposts requests
        driver.scopes = [r'.*maps/rpc/listugcposts.*']
        print("Set request scope to specifically target review API endpoints")
        
        # Scroll to trigger more review loads
        print(f"Starting to scroll with {cfg.scroll_iterations} iterations...")
        for i in range(cfg.scroll_iterations):  # Use the configurable parameter
            if review_container:
                # Scroll within the container
                driver.execute_script("""document.querySelector('div[jslog="26354;mutable:true;"]').scrollBy(0, 10000)""")
                print(f"Scrolled review container (iteration {i+1}/{cfg.scroll_iterations})")
            else:
                # Fallback to global scrolling
                driver.execute_script("""window.scrollBy(0, 10000)""")
                print(f"Scrolled window (iteration {i+1}/{cfg.scroll_iterations})")
            
            # Wait longer between scrolls to allow requests to complete
            time.sleep(2)
        
        # Print the captured review API requests
        print(f"Captured {len(driver.requests)} requests after filtering for review API endpoints")
        # Process review API requests
        for request in driver.requests:
            if "listugcposts" in request.url and request.response:
                print(f"Request URL: {request.url}")
                response_body = request.response.body
                if not response_body:
                    continue
                    
                print(f"Processing review API response from: {request.url}")
                
                try:
                    # Process the brotli-compressed response
                    reviews = extract_reviews_from_api(response_body)
                    print(f"Extracted {len(reviews)} reviews from response")
                    all_reviews.extend(reviews)
                except Exception as e:
                    print(f"Error processing response: {str(e)}")
                    continue
        
        if len(all_reviews) == 0:
            print("WARNING: No reviews were captured. Broadening search...")
            # If no reviews found with specific endpoint, try all requests
            for request in driver.requests:
                if request.response and "listugcposts" in request.url:
                    try:
                        response_body = request.response.body
                        if not response_body:
                            continue
                            
                        print(f"Attempting to process: {request.url}")
                        # Save raw response for debugging
                        with open(f"raw_response.bin", "wb") as f:
                            f.write(response_body)
                            
                        try:
                            reviews = extract_reviews_from_api(response_body)
                            if reviews:
                                print(f"Found {len(reviews)} reviews!")
                                all_reviews.extend(reviews)
                        except Exception as e:
                            print(f"Failed to extract reviews: {str(e)}")
                    except Exception as e:
                        print(f"Error handling request: {str(e)}")
        
        return all_reviews
        
    finally:
        driver.quit()

def parse_google_maps_response(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the initial markup characters
    if content.startswith(")]}'"):
        content = content[4:]
    
    # Parse the JSON data
    import json
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def extract_reviews(data):
    reviews = []
    
    # Navigate through the nested structure to find reviews
    if data and isinstance(data, list) and len(data) > 2:
        review_blocks = data[2]
        
        for review_block in review_blocks:
            if not review_block or not isinstance(review_block, list) or len(review_block) < 1:
                continue
                
            # Extract basic review info
            try:
                reviewer_name = review_block[0][5][0][0]
                reviewer_profile_url = review_block[0][5][1]
                reviewer_profile_pic = review_block[0][5][2]
                review_date = review_block[0][5][1]
                rating = review_block[0][4]
                
                # Extract review text from the review_block[3] section
                review_text = ""
                if len(review_block) > 3 and review_block[3] and len(review_block[3]) > 0:
                    if review_block[3][0] and len(review_block[3][0]) > 0:
                        review_text = review_block[3][0][0]
                
                # Extract photos if available
                photos = []
                if len(review_block[1]) > 1 and review_block[1][1]:
                    for photo_data in review_block[1][1]:
                        if photo_data and len(photo_data) > 0:
                            photo_url = photo_data[0][6][0]
                            photos.append(photo_url)
                
                review = {
                    "reviewer_name": reviewer_name,
                    "reviewer_profile_url": reviewer_profile_url,
                    "reviewer_profile_pic": reviewer_profile_pic,
                    "date": review_date,
                    "rating": rating,
                    "text": review_text,
                    "photos": photos
                }
                
                reviews.append(review)
                
            except (IndexError, TypeError) as e:
                print(f"Error extracting review data: {e}")
                continue
                
    return reviews