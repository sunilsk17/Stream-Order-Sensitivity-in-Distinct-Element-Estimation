#!/usr/bin/env python3
"""
Plot Real Data Convergence Analysis Results

Generates publication-quality visualizations from real_data_convergence_analysis_results.json
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_results():
    """Load the convergence analysis results."""
    result_file = Path(__file__).parent.parent / 'results' / 'real_data_convergence_analysis_results.json'
    with open(result_file, 'r') as f:
        return json.load(f)


def plot_convergence_curves():
    """Plot convergence curves for each dataset (averaged across orderings)."""
    results = load_results()
    
    # Group experiments by dataset
    datasets = {}
    for exp in results['experiments']:
        dataset = exp['dataset']
        if dataset not in datasets:
            datasets[dataset] = []
        datasets[dataset].append(exp)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Color palette
    colors = {
        'Wikipedia': '#2E86AB',
        'GitHub': '#A23B72',
        'Common Crawl': '#F18F01',
        'Enron': '#C73E1D'
    }
    
    # Plot convergence for each dataset (average across orderings)
    for dataset, experiments in datasets.items():
        # Average convergence across orderings
        num_checkpoints = len(experiments[0]['convergence'])
        avg_errors = np.zeros(num_checkpoints)
        percentages = []
        
        for i in range(num_checkpoints):
            errors = [exp['convergence'][i]['error'] for exp in experiments]
            avg_errors[i] = np.mean(errors)
            percentages.append(experiments[0]['convergence'][i]['pct'])
        
        ax.plot(percentages, avg_errors, marker='o', linewidth=2.5, markersize=6,
                label=dataset, color=colors[dataset], alpha=0.85)
    
    # Formatting
    ax.set_xlabel('Stream Processed (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Relative Error (%)', fontsize=13, fontweight='bold')
    ax.set_title('Convergence Analysis: Estimation Error vs Stream Progression\n(Averaged across stream orderings)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper right', framealpha=0.95)
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'real_data_convergence_curves.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_order_sensitivity():
    """Plot sensitivity factor for each dataset."""
    results = load_results()
    
    # Extract sensitivity summary
    sensitivities = results['sensitivity_summary']
    datasets = [s['dataset'] for s in sensitivities]
    factors = [s['sensitivity'] for s in sensitivities]
    dup_pcts = [s['dup_pct'] for s in sensitivities]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color palette
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # Create bars
    bars = ax.bar(datasets, factors, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, factor, dup) in enumerate(zip(bars, factors, dup_pcts)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{factor:.3f}×\n({dup:.1f}% dup)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Formatting
    ax.set_ylabel('Order Sensitivity Factor\n(Grouped Time / Random Time)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
    ax.set_title('Order Sensitivity Across Real Datasets\n(Lower = Less Sensitive to Stream Order)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0.9, 1.75)
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.6, label='No Order Effect')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'order_sensitivity_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_duplicate_vs_sensitivity():
    """Plot relationship between duplicate ratio and sensitivity."""
    results = load_results()
    
    # Extract data
    sensitivities = results['sensitivity_summary']
    datasets = [s['dataset'] for s in sensitivities]
    dup_pcts = [s['dup_pct'] for s in sensitivities]
    factors = [s['sensitivity'] for s in sensitivities]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Color palette
    colors_map = {
        'Wikipedia': '#2E86AB',
        'GitHub': '#A23B72',
        'Common Crawl': '#F18F01',
        'Enron': '#C73E1D'
    }
    
    # Create scatter plot
    for i, (dataset, dup, factor) in enumerate(zip(datasets, dup_pcts, factors)):
        ax.scatter(dup, factor, s=300, color=colors_map[dataset], 
                  alpha=0.8, edgecolor='black', linewidth=2, label=dataset, zorder=3)
        ax.annotate(dataset, (dup, factor), xytext=(10, 5), textcoords='offset points',
                   fontsize=10, fontweight='bold')
    
    # Add trend line
    z = np.polyfit(dup_pcts, factors, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(min(dup_pcts) - 5, max(dup_pcts) + 5, 100)
    ax.plot(x_trend, p(x_trend), "r--", linewidth=2, alpha=0.5, label='Trend')
    
    # Formatting
    ax.set_xlabel('Data Duplication Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Order Sensitivity Factor', fontsize=12, fontweight='bold')
    ax.set_title('Relationship: Data Duplication vs Stream Order Sensitivity\n(Higher duplication = Higher sensitivity)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-5, 105)
    ax.set_ylim(0.95, 1.65)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'duplicate_vs_sensitivity.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_dataset_characteristics():
    """Create heatmap of dataset characteristics vs convergence metrics."""
    results = load_results()
    
    # Extract summary data
    sensitivities = results['sensitivity_summary']
    datasets_info = results['datasets_info']
    
    # Prepare data for heatmap
    dataset_names = []
    unique_pcts = []
    dup_pcts = []
    sensitivities_list = []
    
    for s in sensitivities:
        dataset_names.append(s['dataset'])
        # Compute unique percentage
        total = datasets_info[s['dataset']]['total']
        unique = datasets_info[s['dataset']]['unique']
        unique_pct = (unique / total) * 100
        unique_pcts.append(unique_pct)
        dup_pcts.append(s['dup_pct'])
        sensitivities_list.append(s['sensitivity'])
    
    # Normalize metrics to 0-100 scale for heatmap
    data_matrix = np.array([
        unique_pcts,
        dup_pcts,
        [s * 50 for s in sensitivities_list]  # Scale sensitivity for visibility
    ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(11, 5))
    
    # Create heatmap
    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # Set ticks
    ax.set_xticks(np.arange(len(dataset_names)))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels(dataset_names, fontsize=11, fontweight='bold')
    ax.set_yticklabels(['Unique Items %', 'Duplicate Ratio %', 'Sensitivity (×50)'], 
                       fontsize=11, fontweight='bold')
    
    # Add text annotations
    for i in range(3):
        for j in range(len(dataset_names)):
            value = data_matrix[i, j]
            if i == 0:
                text = f'{unique_pcts[j]:.1f}%'
            elif i == 1:
                text = f'{dup_pcts[j]:.1f}%'
            else:
                text = f'{sensitivities_list[j]:.3f}×'
            
            ax.text(j, i, text, ha='center', va='center', color='black',
                   fontsize=10, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Normalized Value', rotation=270, labelpad=20, fontsize=10)
    
    # Title
    ax.set_title('Dataset Characteristics: Uniqueness, Duplication, and Order Sensitivity',
                fontsize=13, fontweight='bold', pad=15)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'dataset_characteristics_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_convergence_by_ordering():
    """Create subplots showing convergence for each dataset across orderings."""
    results = load_results()
    
    # Group by dataset
    datasets = {}
    for exp in results['experiments']:
        dataset = exp['dataset']
        if dataset not in datasets:
            datasets[dataset] = {}
        ordering = exp['ordering']
        datasets[dataset][ordering] = exp
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    colors_map = {
        'grouped': '#2E86AB',
        'random': '#C73E1D',
        'chrono': '#F18F01'
    }
    
    dataset_list = list(datasets.keys())
    
    for idx, dataset in enumerate(dataset_list):
        ax = axes[idx]
        
        # Plot each ordering
        for ordering, exp in datasets[dataset].items():
            percentages = [c['pct'] for c in exp['convergence']]
            errors = [c['error'] for c in exp['convergence']]
            
            ax.plot(percentages, errors, marker='o', linewidth=2, markersize=4,
                   label=ordering.capitalize(), color=colors_map[ordering], alpha=0.8)
        
        # Formatting
        ax.set_xlabel('Stream Processed (%)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Relative Error (%)', fontsize=10, fontweight='bold')
        ax.set_title(dataset, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)
        ax.set_ylim(bottom=0)
    
    fig.suptitle('Convergence Analysis by Dataset and Stream Ordering',
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    output_path = Path(__file__).parent / 'convergence_by_ordering.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_final_errors_comparison():
    """Compare final errors across datasets and orderings."""
    results = load_results()
    
    # Group by dataset and ordering
    data_by_ordering = {}
    for exp in results['experiments']:
        ordering = exp['ordering']
        if ordering not in data_by_ordering:
            data_by_ordering[ordering] = {}
        data_by_ordering[ordering][exp['dataset']] = exp['final_error']
    
    # Prepare data for grouped bar chart
    datasets = ['Wikipedia', 'GitHub', 'Common Crawl', 'Enron']
    orderings = sorted(data_by_ordering.keys())
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(datasets))
    width = 0.25
    colors = ['#2E86AB', '#C73E1D', '#F18F01']
    
    for i, ordering in enumerate(orderings):
        errors = [data_by_ordering[ordering][d] for d in datasets]
        ax.bar(x + i*width, errors, width, label=ordering.capitalize(), 
              color=colors[i], alpha=0.85, edgecolor='black', linewidth=1)
    
    # Formatting
    ax.set_xlabel('Dataset', fontsize=12, fontweight='bold')
    ax.set_ylabel('Final Relative Error (%)', fontsize=12, fontweight='bold')
    ax.set_title('Estimation Accuracy: Final Error by Dataset and Stream Ordering',
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x + width)
    ax.set_xticklabels(datasets, fontsize=11, fontweight='bold')
    ax.legend(fontsize=11, title='Stream Ordering', title_fontsize=11)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'final_errors_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


if __name__ == '__main__':
    print("Generating real data convergence analysis plots...")
    plot_convergence_curves()
    plot_order_sensitivity()
    plot_duplicate_vs_sensitivity()
    plot_dataset_characteristics()
    plot_convergence_by_ordering()
    plot_final_errors_comparison()
    print("\nAll real data plots generated successfully! ✓")
