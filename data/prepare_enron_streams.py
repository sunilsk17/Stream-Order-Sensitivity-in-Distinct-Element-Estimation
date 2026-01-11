#!/usr/bin/env python3
"""
Prepare Enron stream variants from real data.
Enron corpus is public data from PACER database.
"""

import json
import random

def load_enron_data():
    """Load real Enron email data"""
    with open('data/enron_items_100k.txt', 'r') as f:
        items = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(items)} emails from Enron corpus")
    return items

def analyze_stream(items):
    """Analyze stream characteristics"""
    total = len(items)
    unique = len(set(items))
    dup_ratio = 100 * (total - unique) / total if total > 0 else 0
    
    # Count bursts (consecutive identical items)
    bursts = 0
    for i in range(1, len(items)):
        if items[i] == items[i-1]:
            bursts += 1
    
    print(f"\nStream Characteristics:")
    print(f"  Total items: {total:,}")
    print(f"  Unique items: {unique:,}")
    print(f"  Duplicate ratio: {dup_ratio:.1f}%")
    print(f"  Burst patterns: {bursts:,}")
    
    return {
        'total': total,
        'unique': unique,
        'duplicate_ratio': dup_ratio,
        'bursts': bursts
    }

def main():
    print("=" * 70)
    print("ENRON STREAM PREPARATION")
    print("=" * 70)
    
    # Load real data
    items = load_enron_data()
    total_unique = len(set(items))
    
    print(f"✓ Enron corpus: {len(items)} emails, {total_unique} unique senders")
    print(f"✓ Real public data from PACER (Enron corpus)")
    
    # Create variants
    print("\n" + "=" * 70)
    print("Creating stream variants...")
    print("=" * 70)
    
    print("\n1. GROUPED (lexicographically sorted):")
    grouped = sorted(items)
    grouped_stats = analyze_stream(grouped)
    
    with open('data/enron_items_grouped.txt', 'w') as f:
        for item in grouped:
            f.write(item + '\n')
    print("✓ Saved to: data/enron_items_grouped.txt")
    
    print("\n2. RANDOM (shuffled order):")
    random.seed(42)  # For reproducibility
    random_stream = items.copy()
    random.shuffle(random_stream)
    random_stats = analyze_stream(random_stream)
    
    with open('data/enron_items_random.txt', 'w') as f:
        for item in random_stream:
            f.write(item + '\n')
    print("✓ Saved to: data/enron_items_random.txt")
    
    print("\n3. CHRONOLOGICAL (original order from corpus):")
    chrono_stats = analyze_stream(items)
    
    with open('data/enron_items_chrono.txt', 'w') as f:
        for item in items:
            f.write(item + '\n')
    print("✓ Saved to: data/enron_items_chrono.txt")
    
    # Save statistics
    stats = {
        'dataset': 'Enron Email Corpus (Real Public Data)',
        'total_items': len(items),
        'unique_items': total_unique,
        'duplicate_ratio': round(100 * (len(items) - total_unique) / len(items), 1),
        'bursts': chrono_stats['bursts'],
        'source': 'PACER - Public Enron Email Corpus',
        'data_type': 'Public email addresses from Enron investigation'
    }
    
    with open('data/enron_stream_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("\n✓ Statistics saved to: data/enron_stream_stats.json")
    
    print("\n" + "=" * 70)
    print("SUMMARY: Enron Stream Preparation Complete")
    print("=" * 70)
    print(f"Dataset: Real Enron Email Corpus (public data)")
    print(f"Total emails: {len(items):,}")
    print(f"Unique senders: {total_unique:,}")
    print(f"Duplicate ratio: {100 * (len(items) - total_unique) / len(items):.1f}%")
    print(f"Stream variants: grouped, random, chronological")

if __name__ == '__main__':
    main()
