# Arsitektur Google Reviews Scraper

```mermaid
graph TD
  A[CLI: main] --> B[Config: Settings]
  B --> C[Driver: init_driver]
  C --> D[Scraper: scrape_reviews]
  D --> E[Parser: scroll_reviews, parse_reviews]
  E --> F[Output: JSON file]
## System Components

### CLI (main.py)
The main entry point of the application that handles command line arguments and controls execution flow.

### Config (settings.py)
Manages application configuration, including target URL, maximum number of reviews, and output settings.

### Driver (driver.py)
Responsible for initializing and managing the Selenium WebDriver for web page interaction.

### Scraper (scraper.py)
Implements the core logic for accessing Google Reviews pages and collecting raw review data.

### Parser (parser.py)
Contains functions for page scrolling and extracting structured data from review HTML elements.

### Output
Processes and saves the scraped data in JSON format.
