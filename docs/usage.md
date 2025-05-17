# Usage

## Installation

You can install the package using pip:

```bash
pip install review_scraper
```

## Basic Usage

To use the review scraper, import the package and initialize a scraper object:

```python
from review_scraper import ReviewScraper

# Initialize the scraper
scraper = ReviewScraper()

# Scrape reviews from a specific URL
reviews = scraper.scrape("https://example.com/product/123")

# Print the results
for review in reviews:
    print(f"Rating: {review.rating}")
    print(f"Title: {review.title}")
    print(f"Content: {review.content}")
    print(f"Author: {review.author}")
    print(f"Date: {review.date}")
    print("---")
```

## Advanced Options

### Filtering Reviews

You can filter reviews based on various criteria:

```python
# Get reviews with rating >= 4
positive_reviews = scraper.scrape("https://example.com/product/123", min_rating=4)

# Get reviews from a specific date range
recent_reviews = scraper.scrape(
    "https://example.com/product/123",
    start_date="2023-01-01",
    end_date="2023-12-31"
)
```

### Exporting Results

Save the scraped reviews to different formats:

```python
# Export to CSV
scraper.export_to_csv(reviews, "product_reviews.csv")

# Export to JSON
scraper.export_to_json(reviews, "product_reviews.json")

# Export to Excel
scraper.export_to_excel(reviews, "product_reviews.xlsx")
```

## Command Line Interface

The package also provides a command-line interface:

```bash
# Basic usage
review-scraper https://example.com/product/123

# Specify output format
review-scraper https://example.com/product/123 --format csv --output reviews.csv

# Filter by rating
review-scraper https://example.com/product/123 --min-rating 4
```

## Configuration

You can create a configuration file to customize the scraper behavior:

```yaml
# config.yaml
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
request_delay: 2
max_retries: 3
timeout: 30
```

Load the configuration:

```python
scraper = ReviewScraper(config_file="config.yaml")
```