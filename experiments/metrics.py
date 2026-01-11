"""
STEP 2: Define Convergence Metrics (Paper-Ready)

Convert raw data into publishable metrics and visualizations.
These form the core empirical contribution.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.convergence import run_convergence_experiment, load_stream


def generate_convergence_metrics_report(stream_path, output_dir='results'):
    """
    Generate paper-ready metrics report.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Run full convergence analysis
    results = run_convergence_experiment(stream_path, num_runs=3)
    
    # Extract metrics into structured format
    metrics_report = {
        'title': 'Convergence Behavior in Distinct Element Sketches',
        'dataset': {
            'stream_size': 100000,
            'actual_cardinality': 16704,
            'distribution': 'Correlated (80/20 hot-set/long-tail)',
        },
        'metrics': {}
    }
    
    # METRIC 1: Time to Target Accuracy
    print("\n" + "="*70)
    print("STEP 2: CONVERGENCE METRICS (Paper-Ready)")
    print("="*70 + "\n")
    
    print("METRIC 1: Time-to-Accuracy (position where error < 5%)")
    print("-" * 70)
    
    time_to_accuracy = {}
    for order_name in ['original', 'random', 'grouped']:
        hll_time = results[order_name]['hll']['metrics'].get('time_to_5_percent')
        time_to_accuracy[order_name] = {
            'position': hll_time,
            'fraction_of_stream': hll_time / 100000 if hll_time else None,
            'items_remaining': 100000 - hll_time if hll_time else None
        }
        print(f"\n{order_name.upper()}:")
        print(f"  Position:           {hll_time:.0f} items")
        print(f"  % of stream:        {(hll_time/100000)*100:.1f}%")
        print(f"  Items until target: {100000 - hll_time:.0f}")
    
    # Buffered comparison
    if 'buffered_grouped' in results:
        buffered_metrics = results['buffered_grouped'].get('metrics', {})
        buffered_time = buffered_metrics.get('time_to_5_percent')
        if buffered_time:
            print(f"\nBUFFERED (grouped):")
            print(f"  Position:           {buffered_time:.0f} items")
            print(f"  % of stream:        {(buffered_time/100000)*100:.1f}%")
    
    metrics_report['metric1_time_to_accuracy'] = time_to_accuracy
    
    # METRIC 2: Early-Stage Error Profile
    print("\n" + "="*70)
    print("METRIC 2: Early-Stage Error Profile")
    print("-" * 70)
    
    early_stage = {}
    for order_name in ['original', 'random', 'grouped']:
        metrics = results[order_name]['hll']['metrics']
        early_stage[order_name] = {
            'error_at_10_percent': metrics.get('early_10_percent_error'),
            'error_at_25_percent': metrics.get('early_25_percent_error'),
            'error_at_50_percent': metrics.get('early_50_percent_error'),
            'final_error': metrics.get('final_error')
        }
        
        print(f"\n{order_name.upper()}:")
        print(f"  10% of stream:    {metrics.get('early_10_percent_error')*100:.2f}%")
        print(f"  25% of stream:    {metrics.get('early_25_percent_error')*100:.2f}%")
        print(f"  50% of stream:    {metrics.get('early_50_percent_error')*100:.2f}%")
        print(f"  Final (100%):     {metrics.get('final_error')*100:.2f}%")
    
    metrics_report['metric2_early_stage_error'] = early_stage
    
    # METRIC 3: Convergence Stability
    print("\n" + "="*70)
    print("METRIC 3: Convergence Stability (Error Std Dev)")
    print("-" * 70)
    
    stability = {}
    for order_name in ['original', 'random', 'grouped']:
        metrics = results[order_name]['hll']['metrics']
        stability[order_name] = metrics.get('error_stability')
        
        print(f"\n{order_name.upper()}:  {metrics.get('error_stability')*100:.4f}%")
    
    metrics_report['metric3_stability'] = stability
    
    # METRIC 4: Order Sensitivity Factor (NEW)
    print("\n" + "="*70)
    print("METRIC 4: Order Sensitivity Factor")
    print("-" * 70)
    
    grouped_time = time_to_accuracy['grouped']['position']
    random_time = time_to_accuracy['random']['position']
    
    sensitivity_factor = random_time / grouped_time if grouped_time > 0 else 0
    
    print(f"\nRandom order time-to-accuracy / Grouped order time-to-accuracy:")
    print(f"  = {random_time:.0f} / {grouped_time:.0f}")
    print(f"  = {sensitivity_factor:.2f}×")
    print(f"\n  INTERPRETATION: Random order takes {sensitivity_factor:.1f}× longer to reach")
    print(f"                  target accuracy than grouped order!")
    print(f"  This is the quantitative ORDER SENSITIVITY EFFECT.")
    
    metrics_report['metric4_order_sensitivity_factor'] = {
        'random_vs_grouped': sensitivity_factor,
        'interpretation': f'Grouped order converges {sensitivity_factor:.1f}x faster than random'
    }
    
    # METRIC 5: Convergence Delay (NEW)
    print("\n" + "="*70)
    print("METRIC 5: Convergence Delay")
    print("-" * 70)
    
    original_time = time_to_accuracy['original']['position']
    grouped_time = time_to_accuracy['grouped']['position']
    delay = original_time - grouped_time
    delay_pct = (delay / original_time) * 100
    
    print(f"\nDelay for original order vs grouped order:")
    print(f"  Original:  {original_time:.0f} items")
    print(f"  Grouped:   {grouped_time:.0f} items")
    print(f"  Delay:     {delay:.0f} items ({delay_pct:.1f}%)")
    print(f"\n  Systems must process extra {delay:.0f} items to reach 5% accuracy")
    print(f"  in random/original order vs grouped order!")
    
    metrics_report['metric5_convergence_delay'] = {
        'extra_items_original': delay,
        'extra_items_percentage': delay_pct
    }
    
    # Save report as JSON
    report_path = os.path.join(output_dir, 'STEP2_convergence_metrics.json')
    with open(report_path, 'w') as f:
        json.dump(metrics_report, f, indent=2)
    print(f"\n✓ Metrics saved to: {report_path}")
    
    return metrics_report


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    stream_path = os.path.join(project_root, "data", "stream.txt")
    
    metrics = generate_convergence_metrics_report(stream_path)
    
    print("\n" + "="*70)
    print("STEP 2 COMPLETE: Paper-ready metrics generated!")
    print("="*70 + "\n")
