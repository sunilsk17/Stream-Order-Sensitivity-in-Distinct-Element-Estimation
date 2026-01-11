#!/usr/bin/env python3
"""
Extract Enron Data Streams for Cardinality Experiments
======================================================

Takes the full Enron email stream (517K items) and extracts
clean experimental streams with controlled characteristics matching
Common Crawl experiments.

Outputs:
1. enron_items_100k.txt - First 100K items (chronological)
2. enron_items_100k_random.txt - Shuffled version for baseline
3. Stream statistics for reference
"""

import gzip
import json
import random
import os
from collections import defaultdict
from datetime import datetime

ENRON_STREAM_PATH = "/Users/sunilkumars/Desktop/distinct-order-study/data/enron_email_stream.json.gz"
OUTPUT_DIR = "/Users/sunilkumars/Desktop/distinct-order-study/data"
STREAM_SIZE = 100000  # Match Common Crawl experiments

def load_enron_stream():
    """Load Enron email stream from compressed JSON"""
    items = []
    print(f"🔄 Loading Enron stream from {ENRON_STREAM_PATH}...")
    
    with gzip.open(ENRON_STREAM_PATH, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= STREAM_SIZE:
                break
            try:
                record = json.loads(line)
                items.append(record['sender'])
            except:
                continue
    
    print(f"✓ Loaded {len(items)} items")
    return items

def analyze_stream(items, name="Stream"):
    """Analyze stream characteristics"""
    unique = set(items)
    unique_count = len(unique)
    item_counts = defaultdict(int)
    for item in items:
        item_counts[item] += 1
    
    # Burst detection
    bursts = 0
    burst_lengths = []
    last_item = None
    burst_len = 1
    
    for item in items:
        if item == last_item:
            burst_len += 1
        else:
            if burst_len > 1:
                bursts += 1
                burst_lengths.append(burst_len)
            last_item = item
            burst_len = 1
    
    if burst_len > 1:
        bursts += 1
        burst_lengths.append(burst_len)
    
    stats = {
        'name': name,
        'total_items': len(items),
        'unique_items': unique_count,
        'unique_ratio': unique_count / len(items),
        'duplicate_ratio': 1.0 - (unique_count / len(items)),
        'duplicates': len(items) - unique_count,
        'bursts': bursts,
        'avg_burst_length': sum(burst_lengths) / len(burst_lengths) if burst_lengths else 0,
        'max_burst_length': max(burst_lengths) if burst_lengths else 0,
        'top_10_items': sorted([(item, item_counts[item]) for item in list(unique)[:10]],
                              key=lambda x: x[1], reverse=True) if len(unique) > 0 else []
    }
    
    return stats

def write_stream(items, filepath, description):
    """Write stream to file (one item per line)"""
    print(f"\n💾 Writing {description}...")
    print(f"   File: {filepath}")
    print(f"   Items: {len(items):,}")
    
    with open(filepath, 'w') as f:
        for item in items:
            f.write(item + '\n')
    
    file_size = os.path.getsize(filepath) / 1024
    print(f"   Size: {file_size:.2f} KB")
    print(f"   ✓ Written")

def main():
    print("="*70)
    print("ENRON STREAM EXTRACTION FOR CARDINALITY EXPERIMENTS")
    print("="*70)
    
    # Load stream
    items = load_enron_stream()
    
    # Analyze original (chronological)
    print("\n📊 Analyzing chronological stream...")
    stats_chrono = analyze_stream(items, "Enron Chronological")
    print(f"   Total items: {stats_chrono['total_items']:,}")
    print(f"   Unique items: {stats_chrono['unique_items']:,}")
    print(f"   Unique ratio: {stats_chrono['unique_ratio']:.2%}")
    print(f"   Duplicate ratio: {stats_chrono['duplicate_ratio']:.2%}")
    print(f"   Burst patterns: {stats_chrono['bursts']:,}")
    print(f"   Avg burst length: {stats_chrono['avg_burst_length']:.2f}")
    
    # Create random shuffled version
    print(f"\n🔄 Creating randomized version...")
    items_random = items.copy()
    random.shuffle(items_random)
    
    stats_random = analyze_stream(items_random, "Enron Randomized")
    print(f"   Total items: {stats_random['total_items']:,}")
    print(f"   Unique items: {stats_random['unique_items']:,}")
    print(f"   Duplicate ratio: {stats_random['duplicate_ratio']:.2%}")
    
    # Write files
    chrono_file = os.path.join(OUTPUT_DIR, "enron_items_100k.txt")
    random_file = os.path.join(OUTPUT_DIR, "enron_items_100k_random.txt")
    
    write_stream(items, chrono_file, "Chronological Enron Stream")
    write_stream(items_random, random_file, "Randomized Enron Stream")
    
    # Write statistics
    stats_file = os.path.join(OUTPUT_DIR, "enron_stream_stats.json")
    print(f"\n💾 Writing statistics to {stats_file}...")
    
    stats_combined = {
        'timestamp': datetime.now().isoformat(),
        'chronological': stats_chrono,
        'randomized': stats_random,
        'notes': [
            'Enron dataset: 517K emails from 150 Enron employees',
            'Extraction: First 100K items maintaining timestamps',
            'Duplicates: 96% - highly concentrated distribution',
            'Bursts: Natural email activity patterns',
            'Comparison: Enron shows realistic clustering vs Common Crawl (unique URLs)'
        ]
    }
    
    import json
    with open(stats_file, 'w') as f:
        json.dump(stats_combined, f, indent=2)
    
    print(f"✓ Saved")
    
    print(f"\n✅ ENRON STREAM EXTRACTION COMPLETE!")
    print(f"\n📁 Output files:")
    print(f"   {chrono_file}")
    print(f"   {random_file}")
    print(f"   {stats_file}")
    
    print(f"\n🔬 Ready for Phase 2 experiments!")
    print(f"   Use chronological stream with:")
    print(f"   - Clustered/Grouped order (natural bursts)")
    print(f"   - Random order (shuffled baseline)")
    print(f"   Expected outcome: ~2.0x sensitivity on bursty data")

if __name__ == "__main__":
    main()
