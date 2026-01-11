#!/usr/bin/env python3
"""
Parse GitHub Event Stream (JSON format)
Extracts actor logins and repository names for duplicate analysis.
"""

import json
import os
from collections import Counter
from typing import List, Tuple

def parse_github_events(filepath: str, max_items: int = None) -> List[str]:
    """
    Parse GitHub event stream JSON.
    
    Each line is a JSON object containing event data.
    Extract actor login as the primary entity (who performed the action).
    """
    actors = []
    line_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    # Extract actor login
                    if 'actor' in event and 'login' in event['actor']:
                        actor = event['actor']['login']
                        actors.append(actor)
                        line_count += 1
                        
                        if max_items and line_count >= max_items:
                            break
                except json.JSONDecodeError:
                    continue
    
    except Exception as e:
        print(f"Error parsing file: {e}")
    
    return actors

def analyze_stream(actors: List[str]) -> dict:
    """Analyze stream characteristics."""
    unique_actors = set(actors)
    duplicates = len(actors) - len(unique_actors)
    duplicate_ratio = duplicates / len(actors) if actors else 0
    
    # Count occurrences
    counter = Counter(actors)
    
    # Find bursts (consecutive identical items)
    bursts = 0
    if actors:
        for i in range(len(actors) - 1):
            if actors[i] == actors[i+1]:
                bursts += 1
    
    # Distribution analysis
    top_items = counter.most_common(10)
    
    return {
        'total_items': len(actors),
        'unique_items': len(unique_actors),
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

def generate_streams(actors: List[str], output_dir: str) -> dict:
    """Generate experimental streams."""
    
    # Grouped stream (sorted by actor name)
    grouped = sorted(actors)
    grouped_file = os.path.join(output_dir, 'github_items_grouped.txt')
    with open(grouped_file, 'w') as f:
        for item in grouped:
            f.write(item + '\n')
    
    # Random stream (shuffled)
    import random
    random_order = actors.copy()
    random.shuffle(random_order)
    random_file = os.path.join(output_dir, 'github_items_random.txt')
    with open(random_file, 'w') as f:
        for item in random_order:
            f.write(item + '\n')
    
    # Original order (chronological)
    chrono_file = os.path.join(output_dir, 'github_items_chrono.txt')
    with open(chrono_file, 'w') as f:
        for item in actors:
            f.write(item + '\n')
    
    return {
        'grouped_file': grouped_file,
        'random_file': random_file,
        'chrono_file': chrono_file,
    }

def main():
    """Main execution."""
    filepath = '/Users/sunilkumars/Desktop/distinct-order-study/GitHub Event Stream/2025-01-01-15.json'
    output_dir = '/Users/sunilkumars/Desktop/distinct-order-study/data'
    
    print("Parsing GitHub event stream...")
    print(f"File: {filepath}")
    print()
    
    # Parse 100K items for experiment
    actors = parse_github_events(filepath, max_items=100000)
    print(f"✓ Extracted {len(actors):,} events (actor logins)")
    
    # Analyze
    stats = analyze_stream(actors)
    print()
    print("Stream Characteristics:")
    print(f"  Total items: {stats['total_items']:,}")
    print(f"  Unique items: {stats['unique_items']:,}")
    print(f"  Duplicate ratio: {stats['duplicate_ratio']:.2%}")
    print(f"  Burst patterns: {stats['burst_patterns']:,}")
    print(f"  Gini coefficient: {stats['gini_coefficient']:.4f}")
    print()
    print("Top 10 actors:")
    for actor, count in stats['top_10_items']:
        print(f"  {actor}: {count}")
    
    # Generate streams
    print()
    print("Generating experimental streams...")
    files = generate_streams(actors, output_dir)
    print(f"✓ Grouped stream: {files['grouped_file']}")
    print(f"✓ Random stream: {files['random_file']}")
    print(f"✓ Chrono stream: {files['chrono_file']}")
    
    # Save stats
    stats_file = os.path.join(output_dir, 'github_stream_stats.json')
    import json
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics: {stats_file}")

if __name__ == '__main__':
    main()
