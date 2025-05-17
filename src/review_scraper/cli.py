import click
from .scraper import scrape_reviews
from .config import Settings

@click.command()
@click.option('--url',     required=True, help="Google Maps place URL")
@click.option('--stars',   default=None,   help="Filter bintang, e.g. 4 or 3,5")
@click.option('--output',  default="out.json", help="Path file output JSON")
@click.option('--headless/--no-headless', default=True)
def main(url, stars, output, headless):
    cfg = Settings(
        place_url=url,
        star_filter=[int(s) for s in stars.split(',')] if stars else None,
        output_path=output,
        headless=headless
    )
    scrape_reviews(cfg)

if __name__ == '__main__':
    main()
