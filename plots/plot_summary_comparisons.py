#!/usr/bin/env python3
"""
Plot Summary and Comparison Visualizations

Cross-experiment analysis and comprehensive comparisons
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_real_results():
    """Load real data convergence analysis results."""
    result_file = Path(__file__).parent.parent / 'results' / 'real_data_convergence_analysis_results.json'
    with open(result_file, 'r') as f:
        return json.load(f)


def load_synthetic_results():
    """Load synthetic correlation analysis results."""
    result_file = Path(__file__).parent.parent / 'results' / 'synthetic_correlation_analysis_results.json'
    with open(result_file, 'r') as f:
        return json.load(f)


def load_zipfian_results():
    """Load zipfian distribution analysis results."""
    result_file = Path(__file__).parent.parent / 'results' / 'zipfian_distribution_analysis_results.json'
    with open(result_file, 'r') as f:
        return json.load(f)


def plot_metrics_summary_table():
    """Create a publication-quality summary table of key metrics."""
    real_results = load_real_results()
    
    # Extract data
    sensitivities = real_results['sensitivity_summary']
    datasets_info = real_results['datasets_info']
    
    # Prepare table data
    table_data = []
    for s in sensitivities:
        dataset = s['dataset']
        info = datasets_info[dataset]
        table_data.append([
            dataset,
            f"{info['total']:,}",
            f"{info['unique']:,}",
            f"{s['dup_pct']:.1f}%",
            f"{s['sensitivity']:.3f}×"
        ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('off')
    
    # Column headers
    headers = ['Dataset', 'Total Items', 'Unique Items', 'Duplicates %', 'Sensitivity Factor']
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers,
                    cellLoc='center', loc='center',
                    colWidths=[0.15, 0.15, 0.15, 0.15, 0.15])
    
    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style headers
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white')
    
    # Style rows with alternating colors
    colors = ['#E8F4F8', '#FFFFFF']
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            cell.set_facecolor(colors[i % 2])
            cell.set_edgecolor('black')
            cell.set_linewidth(1)
            
            # Bold the sensitivity column
            if j == 4:
                cell.set_text_props(weight='bold')
    
    ax.set_title('Key Metrics Summary: Real Data Analysis\n', 
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'metrics_summary_table.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_sensitivity_heatmap_all_dimensions():
    """Create a comprehensive heatmap showing sensitivity across different dimensions."""
    real_results = load_real_results()
    
    # Extract real data sensitivities
    real_data = {}
    for s in real_results['sensitivity_summary']:
        real_data[s['dataset']] = s['sensitivity']
    
    # Get synthetic data (use middle and high correlation points)
    synthetic_results = load_synthetic_results()
    synthetic_points = synthetic_results['analysis']
    
    # Create synthetic categories
    synthetic_categories = []
    synthetic_sensitivities = []
    for point in synthetic_points:
        frac = point['hot_fraction']
        if frac in [0.2, 0.4, 0.6, 0.8, 0.95]:
            synthetic_categories.append(f"Synth-{frac:.0%}")
            synthetic_sensitivities.append(point['sensitivity_factor'])
    
    # Prepare data for visualization
    all_sources = []
    all_categories = []
    all_sensitivities = []
    
    # Add real data
    for dataset, sens in real_data.items():
        all_sources.append('Real Data')
        all_categories.append(dataset)
        all_sensitivities.append(sens)
    
    # Add synthetic data
    for cat, sens in zip(synthetic_categories, synthetic_sensitivities):
        all_sources.append('Synthetic')
        all_categories.append(cat)
        all_sensitivities.append(sens)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Prepare heatmap data
    unique_sources = list(set(all_sources))
    unique_categories = []
    for src in all_sources:
        for cat in all_categories:
            if cat not in unique_categories:
                unique_categories.append(cat)
    
    # Create matrix
    matrix = np.zeros((len(unique_sources), len(unique_categories)))
    for i, src in enumerate(unique_sources):
        for j, cat in enumerate(unique_categories):
            for s, c, sens in zip(all_sources, all_categories, all_sensitivities):
                if s == src and c == cat:
                    matrix[i, j] = sens
                    break
    
    # Plot
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=1.0, vmax=5.5)
    
    # Set ticks
    ax.set_xticks(np.arange(len(unique_categories)))
    ax.set_yticks(np.arange(len(unique_sources)))
    ax.set_xticklabels(unique_categories, fontsize=10, fontweight='bold', rotation=45, ha='right')
    ax.set_yticklabels(unique_sources, fontsize=11, fontweight='bold')
    
    # Add text annotations
    for i in range(len(unique_sources)):
        for j in range(len(unique_categories)):
            if matrix[i, j] > 0:
                text = ax.text(j, i, f'{matrix[i, j]:.2f}×',
                             ha='center', va='center', color='black',
                             fontsize=11, fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Order Sensitivity Factor', rotation=270, labelpad=20, fontsize=11)
    
    ax.set_title('Sensitivity Across All Experiments: Real Data vs Synthetic Data',
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'sensitivity_heatmap_comprehensive.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_dataset_size_vs_sensitivity():
    """Plot relationship between dataset size and sensitivity."""
    real_results = load_real_results()
    
    sensitivities = real_results['sensitivity_summary']
    datasets_info = real_results['datasets_info']
    
    # Extract data
    datasets = []
    sizes = []
    sensitivities_list = []
    
    for s in sensitivities:
        dataset = s['dataset']
        datasets.append(dataset)
        sizes.append(datasets_info[dataset]['total'])
        sensitivities_list.append(s['sensitivity'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color mapping
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # Scatter plot
    for dataset, size, sens, color in zip(datasets, sizes, sensitivities_list, colors):
        ax.scatter(size, sens, s=400, color=color, alpha=0.8, edgecolor='black', 
                  linewidth=2, label=dataset, zorder=3)
    
    # Add labels
    for dataset, size, sens in zip(datasets, sizes, sensitivities_list):
        ax.annotate(dataset, (size, sens), xytext=(10, 5), textcoords='offset points',
                   fontsize=10, fontweight='bold')
    
    # Formatting
    ax.set_xlabel('Dataset Size (Total Items)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Order Sensitivity Factor', fontsize=12, fontweight='bold')
    ax.set_title('Dataset Size vs Order Sensitivity\n(Larger datasets not necessarily more sensitive)',
                fontsize=13, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('linear')
    ax.set_ylim(0.95, 1.65)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'dataset_size_vs_sensitivity.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_main_findings_summary():
    """Create an infographic summarizing main findings."""
    real_results = load_real_results()
    
    sensitivities = real_results['sensitivity_summary']
    
    # Extract key metrics
    max_sens_idx = np.argmax([s['sensitivity'] for s in sensitivities])
    min_sens_idx = np.argmin([s['sensitivity'] for s in sensitivities])
    
    max_dataset = sensitivities[max_sens_idx]['dataset']
    max_sensitivity = sensitivities[max_sens_idx]['sensitivity']
    max_dup = sensitivities[max_sens_idx]['dup_pct']
    
    min_dataset = sensitivities[min_sens_idx]['dataset']
    min_sensitivity = sensitivities[min_sens_idx]['sensitivity']
    min_dup = sensitivities[min_sens_idx]['dup_pct']
    
    # Create figure with text
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # Title
    fig.text(0.5, 0.95, 'Stream Order Sensitivity: Main Findings', 
            ha='center', fontsize=18, fontweight='bold')
    
    # Key Finding 1
    y_pos = 0.85
    fig.text(0.1, y_pos, '1. Maximum Sensitivity', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#C73E1D', alpha=0.3, pad=0.5))
    fig.text(0.1, y_pos - 0.08, f'   Dataset: {max_dataset}\n   Sensitivity Factor: {max_sensitivity:.3f}×\n   Duplication Rate: {max_dup:.1f}%',
            fontsize=11, family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Key Finding 2
    y_pos = 0.65
    fig.text(0.1, y_pos, '2. Minimum Sensitivity', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#2E86AB', alpha=0.3, pad=0.5))
    fig.text(0.1, y_pos - 0.08, f'   Dataset: {min_dataset}\n   Sensitivity Factor: {min_sensitivity:.3f}×\n   Duplication Rate: {min_dup:.1f}%',
            fontsize=11, family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Key Finding 3
    y_pos = 0.45
    fig.text(0.5, y_pos, '3. Critical Insight', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#F18F01', alpha=0.3, pad=0.5))
    fig.text(0.5, y_pos - 0.08,
            'Order Sensitivity is directly correlated with data duplication rate.\nHighly duplicated datasets (like Enron at 97%) experience\n1.583× slowdown when processing random-order streams vs grouped-order.',
            fontsize=11, ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Key Finding 4
    y_pos = 0.15
    fig.text(0.5, y_pos, '4. Practical Recommendation', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#90EE90', alpha=0.3, pad=0.5))
    fig.text(0.5, y_pos - 0.08,
            'For skewed distributions and high-duplication datasets,\ndata pre-sorting provides significant performance benefits (up to 58.3%).',
            fontsize=11, ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'main_findings_summary.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


if __name__ == '__main__':
    print("Generating summary and comparison plots...")
    plot_metrics_summary_table()
    plot_sensitivity_heatmap_all_dimensions()
    plot_dataset_size_vs_sensitivity()
    plot_main_findings_summary()
    print("\nAll summary plots generated successfully! ✓")
