# Google Reviews Scraper

A Python-based scraper for extracting Google Maps reviews from a specified place URL. Built with Selenium and managed with Poetry for reproducibility and ease of maintenance.

## Features
- Headless browser scraping (Chrome)
- Export data in JSON or CSV format
- Sort reviews by date (newest or oldest first)
- Configurable scroll iterations to control how many reviews to fetch
- Environment-based configuration via `.env`
- CLI interface with Click
- Structured modular code for easy testing and extension

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/aliepratama/gmaps-review-scraper.git
   cd gmaps-review-scraper
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```
3. Copy the example environment file and adjust values:

   ```bash
   cp .env.example .env
   # then edit .env to include your target URL and options
   ```

## Usage

Run the CLI command:

```bash
poetry run reviewscraper --url "https://maps.app.goo.gl/YourPlaceShortLink" \
  --output reviews.json --no-headless
```

Or load settings from `.env` and run:

```bash
poetry run reviewscraper
```

## Project Structure

Refer to [docs/architecture.md](docs/architecture.md) for full details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
