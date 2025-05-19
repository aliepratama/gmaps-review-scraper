import click
from .api_scraper import scrape_reviews_api
from .config import Settings

@click.command()
@click.option('--url',     required=True, help="Google Maps place URL")
@click.option('--sort',    default="desc", type=click.Choice(['asc', 'desc']), 
              help="Sort reviews by date (asc=oldest first, desc=newest first)")
@click.option('--iter',    default=15, type=int, help="Number of scroll iterations to load more reviews")
@click.option('--output',  default="out.json", help="Path file output JSON")
@click.option('--headless/--no-headless', default=True)
def main(url, sort, iter, output, headless):
    cfg = Settings(
        place_url=url,
        sort_direction=sort,
        scroll_iterations=iter,
        output_path=output,
        headless=headless
    )
    
    data = scrape_reviews_api(cfg)
    
    import json
    with open(cfg.output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] {len(data)} review disimpan di {cfg.output_path}")

if __name__ == '__main__':
    main()
