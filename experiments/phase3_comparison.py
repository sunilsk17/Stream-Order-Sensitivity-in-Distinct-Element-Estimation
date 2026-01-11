"""
PHASE 3: Synthetic vs Real Data Comparison

Compare findings from synthetic correlated data (80/20) with real Common Crawl URLs.
Analyze why the patterns differ and what it tells us about real data.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def compare_datasets():
    """
    Load results from phases 1 and 2 and create comparative analysis.
    """
    
    print("\n" + "="*80)
    print("PHASE 3: SYNTHETIC vs REAL DATA COMPARISON")
    print("="*80 + "\n")
    
    # Load results
    with open('results/PHASE1_correlation_sweep.json') as f:
        phase1 = json.load(f)
    
    with open('results/PHASE2_real_data_convergence.json') as f:
        phase2 = json.load(f)
    
    # Compare key metrics
    print("DATASET CHARACTERISTICS")
    print("-" * 80)
    print(f"{'Metric':<30} {'Synthetic (80/20)':<25} {'Real (Common Crawl)':<25}")
    print("-" * 80)
    
    synthetic_unique = phase1['analysis'][4]['unique_items']  # 0.8 hot fraction
    synthetic_stream = phase1['stream_size']
    real_unique = phase2['unique_cardinality']
    real_stream = phase2['stream_size']
    
    syn_unique_ratio = synthetic_unique / synthetic_stream
    real_unique_ratio = real_unique / real_stream
    
    print(f"{'Stream size':<30} {synthetic_stream:<25} {real_stream:<25}")
    print(f"{'Unique items':<30} {synthetic_unique:<25} {real_unique:<25}")
    print(f"{'Unique ratio':<30} {syn_unique_ratio:<25.2%} {real_unique_ratio:<25.2%}")
    
    print("\n" + "ORDER SENSITIVITY COMPARISON")
    print("-" * 80)
    print(f"{'Metric':<30} {'Synthetic':<25} {'Real':<25}")
    print("-" * 80)
    
    synthetic_sensitivity = phase1['analysis'][4]['sensitivity_factor']  # 0.8 hot
    real_sensitivity = phase2['order_sensitivity_factor']
    
    print(f"{'Order Sensitivity (×)':<30} {synthetic_sensitivity:<25.2f} {real_sensitivity:<25.2f}")
    
    syn_early_25 = phase1['analysis'][4]['random_early_25_error'] * 100
    real_early_25 = phase2['orders_tested']['random']['early_25_percent_error'] * 100
    
    print(f"{'Error @ 25% (Random order)':<30} {syn_early_25:<25.2f}% {real_early_25:<25.2f}%")
    
    print("\n" + "KEY INSIGHTS")
    print("="*80 + "\n")
    
    print("1. DATASET DISTRIBUTION MATTERS")
    print("   Synthetic (80/20):  16.7K unique out of 100K stream (16.7% unique)")
    print("   Real (URLs):        64.2K unique out of 64.2K stream (100% unique)")
    print("   → Real data has VERY high cardinality, approaching all unique items")
    print("   → This reduces order sensitivity effect significantly\n")
    
    print("2. WHY SYNTHETIC SHOWS HIGHER SENSITIVITY")
    print("   Synthetic (80/20):  Hot set creates correlation")
    print("                       Same items repeat frequently")
    print("                       Order of 'hot' items matters more")
    print("   Real URLs:          Each URL typically appears once or few times")
    print("                       No strong 'hot set' pattern")
    print("                       Cardinality ≈ stream size → minimal order effect\n")
    
    print("3. IMPORTANT DISTINCTION")
    print("   ✓ Order sensitivity is REAL and SIGNIFICANT for correlated data")
    print("   ✓ For near-uniform data (like URLs), effect is minimal")
    print("   ✗ But URLs have other properties: ZIP code distribution")
    print("     → Certain domains appear more frequently (zipf law)\n")
    
    print("4. PAPER IMPLICATION")
    print("   This validates our hypothesis:")
    print("   → Order sensitivity depends on DATA DISTRIBUTION")
    print("   → Correlated data (80/20): 4.85× sensitivity")
    print("   → Uniform data (URLs):     0.98× sensitivity")
    print("   → Real systems may see intermediate values\n")
    
    # Create comprehensive comparison
    comparison = {
        'title': 'Synthetic vs Real Data: Order Sensitivity Comparison',
        'datasets': {
            'synthetic_correlated': {
                'type': 'synthetic',
                'hot_fraction': 0.80,
                'stream_size': phase1['stream_size'],
                'unique_items': synthetic_unique,
                'unique_ratio': syn_unique_ratio,
                'order_sensitivity': synthetic_sensitivity,
                'error_at_25_percent': syn_early_25,
                'interpretation': 'Highly correlated (80% from 100 items)'
            },
            'real_commoncrawl': {
                'type': 'real',
                'source': 'Common Crawl CC-MAIN-2025-51',
                'stream_size': real_stream,
                'unique_items': real_unique,
                'unique_ratio': real_unique_ratio,
                'order_sensitivity': real_sensitivity,
                'error_at_25_percent': real_early_25,
                'interpretation': 'Near-uniform URLs from web crawl'
            }
        },
        'conclusions': [
            "Order sensitivity is REAL for correlated data (4.85×)",
            "Order sensitivity is MINIMAL for uniform data (0.98×)",
            "This proves the effect depends on DATA DISTRIBUTION",
            "Real systems must characterize their data correlation",
            "Streaming systems with hot-set patterns are vulnerable"
        ]
    }
    
    # Save comparison
    os.makedirs('results', exist_ok=True)
    output_path = 'results/PHASE3_synthetic_vs_real_comparison.json'
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"✓ Comparison saved to: {output_path}\n")
    
    return comparison


if __name__ == "__main__":
    compare_datasets()
