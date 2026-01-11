#!/usr/bin/env python3
"""
Parse Wikipedia Pageviews Log
Extracts page names from Wikipedia pageviews data and generates experimental streams.
"""

import gzip
import json
import os
from collections import defaultdict, Counter
from typing import List, Tuple

def parse_pageviews_file(filepath: str, max_items: int = None) -> List[str]:
    """
    Parse Wikipedia pageviews file.
    
    Format: Each line contains fields separated by space:
    domain_code page_title count_views count_bytes
    
    Example: en Wikipedia_Main_Page 123 45678
    """
    pages = []
    line_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 2:
                    # Extract page name (second field)
                    page = parts[1]
                    # Skip special pages
                    if not page.startswith(('Special:', 'MediaWiki:', 'Template:', 'File:')):
                        pages.append(page)
                        line_count += 1
                        
                        if max_items and line_count >= max_items:
                            break
    
    except Exception as e:
        print(f"Error parsing file: {e}")
    
    return pages

def analyze_stream(pages: List[str]) -> dict:
    """Analyze stream characteristics."""
    unique_pages = set(pages)
    duplicates = len(pages) - len(unique_pages)
    duplicate_ratio = duplicates / len(pages) if pages else 0
    
    # Count occurrences
    counter = Counter(pages)
    
    # Find bursts (consecutive identical items)
    bursts = 0
    if pages:
        for i in range(len(pages) - 1):
            if pages[i] == pages[i+1]:
                bursts += 1
    
    # Distribution analysis
    top_items = counter.most_common(10)
    
    return {
        'total_items': len(pages),
        'unique_items': len(unique_pages),
        'duplicate_ratio': round(duplicate_ratio, 4),
        'duplicate_count': duplicates,
        'burst_patterns': bursts,
        'top_10_items': [(item, count) for item, count in top_items],
        'max_count': counter.most_common(1)[0][1] if counter else 0,
        'gini_coefficient': compute_gini(list(counter.values())),
    }

def compute_gini(values: List[int]) -> float:
    """Compute Gini coefficient for distribution inequality."""
    if not values or len(values) < 2:
        return 0.0
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = sum((i + 1) * val for i, val in enumerate(sorted_vals))
    return (2 * cumsum) / (n * sum(values)) - (n + 1) / n

def generate_streams(pages: List[str], output_dir: str) -> dict:
    """Generate experimental streams."""
    
    # Grouped stream (sorted by page name)
    grouped = sorted(pages)
    grouped_file = os.path.join(output_dir, 'wikipedia_items_grouped.txt')
    with open(grouped_file, 'w') as f:
        for item in grouped:
            f.write(item + '\n')
    
    # Random stream (shuffled)
    import random
    random_order = pages.copy()
    random.shuffle(random_order)
    random_file = os.path.join(output_dir, 'wikipedia_items_random.txt')
    with open(random_file, 'w') as f:
        for item in random_order:
            f.write(item + '\n')
    
    # Original order (chronological)
    chrono_file = os.path.join(output_dir, 'wikipedia_items_chrono.txt')
    with open(chrono_file, 'w') as f:
        for item in pages:
            f.write(item + '\n')
    
    return {
        'grouped_file': grouped_file,
        'random_file': random_file,
        'chrono_file': chrono_file,
    }

def main():
    """Main execution."""
    filepath = '/Users/sunilkumars/Desktop/distinct-order-study/Wikipedia Page Request Logs/pageviews-20260101-000000'
    output_dir = '/Users/sunilkumars/Desktop/distinct-order-study/data'
    
    print("Parsing Wikipedia pageviews log...")
    print(f"File: {filepath}")
    print()
    
    # Parse 100K items for experiment
    pages = parse_pageviews_file(filepath, max_items=100000)
    print(f"✓ Extracted {len(pages):,} pageviews")
    
    # Analyze
    stats = analyze_stream(pages)
    print()
    print("Stream Characteristics:")
    print(f"  Total items: {stats['total_items']:,}")
    print(f"  Unique items: {stats['unique_items']:,}")
    print(f"  Duplicate ratio: {stats['duplicate_ratio']:.2%}")
    print(f"  Burst patterns: {stats['burst_patterns']:,}")
    print(f"  Gini coefficient: {stats['gini_coefficient']:.4f}")
    print()
    print("Top 10 pages:")
    for page, count in stats['top_10_items']:
        print(f"  {page}: {count}")
    
    # Generate streams
    print()
    print("Generating experimental streams...")
    files = generate_streams(pages, output_dir)
    print(f"✓ Grouped stream: {files['grouped_file']}")
    print(f"✓ Random stream: {files['random_file']}")
    print(f"✓ Chrono stream: {files['chrono_file']}")
    
    # Save stats
    stats_file = os.path.join(output_dir, 'wikipedia_stream_stats.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics: {stats_file}")

if __name__ == '__main__':
    main()
