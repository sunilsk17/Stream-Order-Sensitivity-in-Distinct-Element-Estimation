#!/usr/bin/env python3
"""
Plot Synthetic Correlation Analysis

Enhanced visualization of how order sensitivity scales with data correlation
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_results():
    """Load synthetic correlation analysis results."""
    result_file = Path(__file__).parent.parent / 'results' / 'synthetic_correlation_analysis_results.json'
    with open(result_file, 'r') as f:
        return json.load(f)


def plot_enhanced_correlation_sweep():
    """Enhanced plot of sensitivity vs correlation with additional details."""
    results = load_results()
    
    # Extract data
    hot_fractions = []
    sensitivities = []
    
    for result in results['analysis']:
        hot_fractions.append(result['hot_fraction'])
        sensitivities.append(result['sensitivity_factor'])
    
    # Create figure with custom styling
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Main plot
    line = ax.plot(hot_fractions, sensitivities, 'o-', linewidth=3, markersize=10, 
                  color='#2E86AB', label='Order Sensitivity Factor', zorder=3)
    
    # Add shaded regions
    ax.axhspan(1.0, 1.1, alpha=0.1, color='green', label='Low Sensitivity (<1.1×)')
    ax.axhspan(1.1, 1.3, alpha=0.1, color='yellow', label='Medium Sensitivity')
    ax.axhspan(1.3, 5.5, alpha=0.1, color='red', label='High Sensitivity (>1.3×)')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    
    # Labels and title
    ax.set_xlabel('Hot-Set Fraction (Data Correlation Level)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Order Sensitivity Factor (Grouped/Random Ratio)', fontsize=13, fontweight='bold')
    ax.set_title('Synthetic Data: Order Sensitivity vs Data Correlation\n(Hot-Set Parameterization)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add value annotations
    for hf, sens in zip(hot_fractions, sensitivities):
        ax.annotate(f'{sens:.2f}×', xy=(hf, sens), xytext=(0, 12), 
                   textcoords='offset points', ha='center', fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    # Axis limits and legend
    ax.set_xlim(0.15, 1.0)
    ax.set_ylim(0.95, 5.5)
    
    # Custom legend
    ax.legend(fontsize=11, loc='upper left', framealpha=0.95)
    
    # Add note about methodology
    ax.text(0.98, 0.02, 'Higher hot-set fraction = More skewed distribution = Higher sensitivity',
           transform=ax.transAxes, fontsize=10, style='italic',
           verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'synthetic_correlation_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_sensitivity_progression():
    """Plot sensitivity progression as correlation increases."""
    results = load_results()
    
    # Extract data
    hot_fractions = []
    sensitivities = []
    
    for result in results['analysis']:
        hot_fractions.append(result['hot_fraction'])
        sensitivities.append(result['sensitivity_factor'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Fill area under curve
    ax.fill_between(hot_fractions, 1.0, sensitivities, alpha=0.2, color='#2E86AB')
    
    # Plot line
    ax.plot(hot_fractions, sensitivities, 'o-', linewidth=2.5, markersize=8,
           color='#2E86AB', label='Sensitivity Factor', zorder=3)
    
    # Reference line at 1.0
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=2, alpha=0.6, label='No Order Effect')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Labels
    ax.set_xlabel('Data Correlation Strength\n(Hot-Set Fraction: 0.2=Uniform, 0.95=Highly Skewed)', 
                 fontsize=12, fontweight='bold')
    ax.set_ylabel('Order Sensitivity Factor', fontsize=12, fontweight='bold')
    ax.set_title('Sensitivity Progression with Increasing Data Correlation',
                fontsize=13, fontweight='bold', pad=15)
    
    ax.set_xlim(0.15, 1.0)
    ax.set_ylim(0.95, max(sensitivities) * 1.1)
    
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'sensitivity_progression.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_gap_analysis():
    """Plot the gap between grouped and random ordering convergence."""
    results = load_results()
    
    # Extract data
    hot_fractions = []
    gaps = []
    
    for result in results['analysis']:
        hot_fractions.append(result['hot_fraction'])
        # Gap = (grouped_time - random_time) / random_time
        sensitivity = result['sensitivity_factor']
        gap = (sensitivity - 1.0) * 100  # Convert to percentage
        gaps.append(gap)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Bar chart
    bars = ax.bar(hot_fractions, gaps, width=0.04, color='#C73E1D', alpha=0.7, 
                 edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, gap in zip(bars, gaps):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{gap:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Grid
    ax.grid(True, axis='y', alpha=0.3)
    
    # Labels
    ax.set_xlabel('Hot-Set Fraction (Data Correlation)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time Overhead (%)\n(Grouped vs Random)', fontsize=12, fontweight='bold')
    ax.set_title('Stream Order Impact: Time Overhead for Grouped vs Random Ordering',
                fontsize=13, fontweight='bold', pad=15)
    
    ax.set_xlim(0.15, 1.05)
    
    plt.tight_layout()
    output_path = Path(__file__).parent / 'order_overhead_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


if __name__ == '__main__':
    print("Generating synthetic correlation analysis plots...")
    plot_enhanced_correlation_sweep()
    plot_sensitivity_progression()
    plot_gap_analysis()
    print("\nAll synthetic analysis plots generated successfully! ✓")
