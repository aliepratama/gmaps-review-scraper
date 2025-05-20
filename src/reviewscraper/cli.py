import click
import csv
import json
from .api_scraper import scrape_reviews_api
from .config import Settings

@click.command()
@click.option('--url',     required=True, help="Google Maps place URL")
@click.option('--sort',    default="desc", type=click.Choice(['asc', 'desc']), 
              help="Sort reviews by date (asc=oldest first, desc=newest first)")
@click.option('--iter',    default=15, type=int, help="Number of scroll iterations to load more reviews")
@click.option('--output',  default="reviews.json", help="Output file path")
@click.option('--format',  default="json", type=click.Choice(['json', 'csv']),
              help="Output file format (json or csv)")
@click.option('--headless/--no-headless', default=True)
def main(url, sort, iter, output, format, headless):
    # Determine output file path with correct extension
    if not output.lower().endswith(f'.{format}'):
        output = f"{output.rsplit('.', 1)[0]}.{format}"
    
    cfg = Settings(
        place_url=url,
        sort_direction=sort,
        scroll_iterations=iter,
        output_path=output,
        headless=headless
    )
    
    data = scrape_reviews_api(cfg)
    
    if format.lower() == 'json':
        with open(cfg.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:  # csv format
        if data and len(data) > 0:
            with open(cfg.output_path, 'w', encoding='utf-8', newline='') as f:
                # Define consistent column headers
                fieldnames = [
                    'reviewer_name', 'reviewer_profile_url', 'reviewer_profile_pic',
                    'stars', 'text', 'date', 'photos'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Process each review with consistent structure
                for review in data:
                    csv_row = {}
                    
                    # Handle reviewer info
                    if 'reviewer' in review and isinstance(review['reviewer'], dict):
                        csv_row['reviewer_name'] = review['reviewer'].get('name', '')
                        csv_row['reviewer_profile_url'] = review['reviewer'].get('profile_url', '')
                        csv_row['reviewer_profile_pic'] = review['reviewer'].get('profile_pic', '')
                    else:
                        csv_row['reviewer_name'] = ''
                        csv_row['reviewer_profile_url'] = ''
                        csv_row['reviewer_profile_pic'] = ''
                    
                    # Copy other fields
                    csv_row['stars'] = review.get('stars', '')
                    csv_row['text'] = review.get('text', '')
                    csv_row['date'] = review.get('date', '')
                    
                    # Convert photos list to comma-separated string
                    if 'photos' in review and isinstance(review['photos'], list):
                        csv_row['photos'] = '; '.join(review['photos'])
                    else:
                        csv_row['photos'] = ''
                    
                    writer.writerow(csv_row)
    
    print(f"[✓] {len(data)} reviews saved to {cfg.output_path}")

if __name__ == '__main__':
    main()
