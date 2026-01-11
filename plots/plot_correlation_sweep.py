#!/usr/bin/env python3
"""
Plot Synthetic Correlation Sweep Results
Shows how order sensitivity scales with data correlation level
"""
import json
import matplotlib.pyplot as plt
import numpy as np

def plot_correlation_sweep():
    """Load correlation sweep results and create figure: Sensitivity vs Correlation"""
    
    # Load results
    with open('results/synthetic_correlation_analysis_results.json', 'r') as f:
        results = json.load(f)
    
    # Extract data
    hot_fractions = []
    sensitivities = []
    
    for result in results['analysis']:
        hot_fractions.append(result['hot_fraction'])
        sensitivities.append(result['sensitivity_factor'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot sensitivity vs correlation
    ax.plot(hot_fractions, sensitivities, 'o-', linewidth=2.5, markersize=8, 
            color='#2E86AB', label='Order Sensitivity Factor')
    
    # Add grid and labels
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('Hot-Set Fraction (Data Correlation Level)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Order Sensitivity Factor (Grouped/Random Ratio)', fontsize=12, fontweight='bold')
    ax.set_title('Synthetic Data Analysis: Order Sensitivity vs Data Correlation\n(Hot-Set Fraction Parameterization)', 
                 fontsize=14, fontweight='bold')
    
    # Add value labels on points
    for hf, sens in zip(hot_fractions, sensitivities):
        ax.annotate(f'{sens:.2f}×', xy=(hf, sens), xytext=(0, 10), 
                   textcoords='offset points', ha='center', fontsize=10, fontweight='bold')
    
    # Set axis limits
    ax.set_xlim(0.15, 1.0)
    ax.set_ylim(1.0, 5.5)
    
    # Add legend
    ax.legend(fontsize=11, loc='upper left')
    
    # Tight layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig('plots/synthetic_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Figure saved: plots/synthetic_correlation_analysis.png")

if __name__ == '__main__':
    plot_correlation_sweep()
