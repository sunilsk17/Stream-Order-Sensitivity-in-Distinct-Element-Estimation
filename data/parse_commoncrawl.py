"""
PHASE 2: Common Crawl WET File Parser

Extract URLs from Common Crawl WET files for real data validation.
WET files contain plain text extracted from web pages.

Format:
WARC/1.0
WARC-Type: conversion
WARC-Target-URI: https://example.com
...
<plain text content>
"""

import os
import sys
import gzip
import re
from pathlib import Path


def parse_wet_file(wet_path, max_items=None, verbose=False):
    """
    Parse a WET file and extract URLs.
    
    Args:
        wet_path: Path to .warc.wet or .warc.wet.gz file
        max_items: Maximum number of items to extract (None = all)
        verbose: Print progress information
    
    Returns:
        List of URLs extracted
    """
    
    urls = []
    current_url = None
    
    # Determine if file is gzipped
    is_gzipped = wet_path.endswith('.gz')
    
    try:
        if is_gzipped:
            opener = gzip.open
        else:
            opener = open
        
        with opener(wet_path, 'rt', errors='ignore') as f:
            for line in f:
                line = line.strip()
                
                # Look for WARC-Target-URI header
                if line.startswith('WARC-Target-URI:'):
                    try:
                        current_url = line.split('WARC-Target-URI:', 1)[1].strip()
                        if current_url and len(current_url) > 5:  # Valid URL
                            urls.append(current_url)
                            
                            if max_items and len(urls) >= max_items:
                                break
                            
                            if verbose and len(urls) % 1000 == 0:
                                print(f"  Extracted {len(urls)} URLs...")
                    except Exception as e:
                        if verbose:
                            print(f"  Warning: Could not parse URL from line: {line[:50]}")
    
    except Exception as e:
        print(f"Error reading file {wet_path}: {e}")
        return []
    
    return urls


def extract_domain(url):
    """Extract domain from URL."""
    try:
        # Simple domain extraction
        if '://' in url:
            url = url.split('://', 1)[1]
        domain = url.split('/')[0].split('?')[0]
        return domain.lower()
    except:
        return url


def main():
    """Main extraction pipeline."""
    
    print("\n" + "="*80)
    print("PHASE 2: COMMON CRAWL WET FILE PARSER")
    print("="*80 + "\n")
    
    # Find all WET files in commoncrawl directory
    crawl_dir = Path(__file__).parent.parent / "commoncrawl"
    
    if not crawl_dir.exists():
        print(f"❌ Crawl directory not found: {crawl_dir}")
        print("   Please run: bash commoncrawl/download.sh")
        return
    
    wet_files = sorted(list(crawl_dir.glob("*.warc.wet")) + list(crawl_dir.glob("*.warc.wet.gz")))
    
    if not wet_files:
        print(f"❌ No WET files found in {crawl_dir}")
        print("   Please run: bash commoncrawl/download.sh")
        return
    
    print(f"Found {len(wet_files)} WET files:\n")
    for f in wet_files:
        size_mb = f.stat().st_size / (1024*1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")
    
    print("\n" + "-"*80)
    print("Extracting URLs...")
    print("-"*80 + "\n")
    
    all_urls = []
    
    for wet_file in wet_files:
        print(f"\nProcessing: {wet_file.name}")
        
        # Extract first 100K URLs from each file
        urls = parse_wet_file(str(wet_file), max_items=100000, verbose=True)
        all_urls.extend(urls)
        
        print(f"  ✓ Extracted {len(urls)} URLs from this file")
        
        # Stop if we have enough data
        if len(all_urls) >= 100000:
            all_urls = all_urls[:100000]
            break
    
    print("\n" + "="*80)
    print(f"TOTAL EXTRACTED: {len(all_urls)} unique URLs")
    print("="*80 + "\n")
    
    # Remove duplicates
    unique_urls = list(set(all_urls))
    print(f"After deduplication: {len(unique_urls)} unique URLs\n")
    
    # Save to stream file
    output_path = Path(__file__).parent.parent / "data" / "stream_commoncrawl.txt"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        for url in unique_urls:
            f.write(url + '\n')
    
    print(f"✓ Saved to: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    # Statistics
    print("\n" + "-"*80)
    print("STATISTICS")
    print("-"*80)
    
    # Extract domains
    domains = [extract_domain(url) for url in unique_urls]
    unique_domains = len(set(domains))
    
    # URL length statistics
    lengths = [len(url) for url in unique_urls]
    
    print(f"Total unique URLs:        {len(unique_urls)}")
    print(f"Unique domains:           {unique_domains}")
    print(f"Average URL length:       {sum(lengths)/len(lengths):.1f} characters")
    print(f"Min URL length:           {min(lengths)} characters")
    print(f"Max URL length:           {max(lengths)} characters")
    
    # Sample URLs
    print(f"\nSample URLs (first 5):")
    for i, url in enumerate(unique_urls[:5], 1):
        print(f"  {i}. {url[:70]}...")
    
    print("\n" + "="*80)
    print("✓ REAL DATA EXTRACTION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Run: python experiments/real_data_convergence_analysis.py")
    print("2. Compare results with synthetic data via synthetic_correlation_analysis.py")
    print("")


if __name__ == "__main__":
    main()
