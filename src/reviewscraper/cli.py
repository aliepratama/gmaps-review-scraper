import click
import csv
import json
import os
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
    
    # Initialize output files with headers
    init_output_file(output, format)
    
    # Create config
    cfg = Settings(
        place_url=url,
        sort_direction=sort,
        scroll_iterations=iter,
        output_path=output,
        headless=headless,
        output_format=format  # Add format to settings
    )
    
    # Call scraper with incremental saving
    total_reviews = scrape_reviews_api(cfg, save_callback=save_reviews_batch)
    
    # Finalize the output file if needed (for JSON we need to close the array)
    if format.lower() == 'json':
        with open(output, 'a', encoding='utf-8') as f:
            f.write('\n]')
    
    print(f"[✓] {total_reviews} reviews saved to {output}")

def init_output_file(output_path, format):
    """Initialize the output file with headers or structure."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    if format.lower() == 'json':
        # For JSON, start with opening bracket
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('[')  # Start JSON array
    else:
        # For CSV, write headers
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'reviewer_name', 'reviewer_profile_url', 'reviewer_profile_pic',
                'stars', 'text', 'date', 'photos'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

def save_reviews_batch(reviews, config, is_first_batch=False):
    """Save a batch of reviews to the output file."""
    if not reviews:
        return 0
    
    # Get the format, defaulting to JSON if not specified
    format = getattr(config, 'output_format', 'json').lower()
    
    # Determine format from file extension if output_format isn't available
    if not hasattr(config, 'output_format') and config.output_path:
        if config.output_path.lower().endswith('.csv'):
            format = 'csv'
        else:
            format = 'json'
    
    if format == 'json':
        with open(config.output_path, 'a', encoding='utf-8') as f:
            for i, review in enumerate(reviews):
                # Add comma before each item except the first item of the first batch
                prefix = "" if is_first_batch and i == 0 else ","
                json_str = json.dumps(review, ensure_ascii=False, indent=2)
                f.write(f"{prefix}\n{json_str}")
    else:  # csv
        with open(config.output_path, 'a', encoding='utf-8', newline='') as f:
            fieldnames = [
                'reviewer_name', 'reviewer_profile_url', 'reviewer_profile_pic',
                'stars', 'text', 'date', 'photos'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            for review in reviews:
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
    
    return len(reviews)

if __name__ == '__main__':
    main()
