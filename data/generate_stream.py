"""
Generate synthetic stream data for initial experiments.
Can be replaced later with real Common Crawl data.
"""

import random
import os

def generate_synthetic_stream(n_elements=100000, n_unique=30000, output_file="stream.txt"):
    """
    Generate a synthetic stream of elements with controlled cardinality.
    
    Args:
        n_elements: Total number of elements in stream
        n_unique: Number of unique elements to draw from
        output_file: Path to output file
    """
    data = [f"item_{random.randint(0, n_unique - 1)}" for _ in range(n_elements)]
    
    # Write to file
    with open(output_file, "w") as f:
        for x in data:
            f.write(x + "\n")
    
    print(f"Generated {n_elements} elements with ~{n_unique} unique items")
    print(f"Actual unique count: {len(set(data))}")
    print(f"Saved to: {output_file}")
    return data


def generate_correlated_stream(n_elements=100000, hot_set_size=100, cold_set_size=50000,
                                hot_ratio=0.8, output_file="stream.txt"):
    """
    STEP 3: Generate correlated stream data.
    
    80% of traffic from small hot set (e.g., popular websites)
    20% from long tail
    
    This exposes order sensitivity effects.
    
    Args:
        n_elements: Total number of elements in stream
        hot_set_size: Number of popular items
        cold_set_size: Number of unpopular items
        hot_ratio: Fraction of traffic from hot set (0.8 = 80%)
        output_file: Path to output file
    """
    hot_items = [f"hot_{i}" for i in range(hot_set_size)]
    cold_items = [f"cold_{i}" for i in range(cold_set_size)]
    
    data = []
    for _ in range(n_elements):
        if random.random() < hot_ratio:
            # 80% from hot set
            data.append(random.choice(hot_items))
        else:
            # 20% from cold set (long tail)
            data.append(random.choice(cold_items))
    
    # Write to file
    with open(output_file, "w") as f:
        for x in data:
            f.write(x + "\n")
    
    unique_count = len(set(data))
    print(f"Generated {n_elements} elements (correlated)")
    print(f"Hot set size: {hot_set_size} items (80% of traffic)")
    print(f"Cold set size: {cold_set_size} items (20% of traffic)")
    print(f"Actual unique count: {unique_count}")
    print(f"Saved to: {output_file}")
    return data


if __name__ == "__main__":
    # Create stream file in the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # STEP 3: Generate correlated stream (for convergence studies)
    output_path = os.path.join(script_dir, "stream.txt")
    print("Generating correlated stream (STEP 3)...\n")
    generate_correlated_stream(output_file=output_path)
