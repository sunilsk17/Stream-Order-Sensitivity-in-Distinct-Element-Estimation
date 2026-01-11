#!/usr/bin/env python3
"""
Plot PHASE 1: Correlation Sweep Results
Shows how order sensitivity scales with data correlation level
"""
import json
import matplotlib.pyplot as plt
import numpy as np

def plot_correlation_sweep():
    """Load PHASE 1 results and create Figure 4: Sensitivity vs Correlation"""
    
    # Load results
    with open('results/PHASE1_correlation_sweep.json', 'r') as f:
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
    ax.set_title('PHASE 1: How Order Sensitivity Scales with Data Correlation\n(Synthetic Data with Parameterized Hot-Set)', 
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
    plt.savefig('plots/PHASE1_correlation_sweep.png', dpi=300, bbox_inches='tight')
    print("✓ Figure saved: plots/PHASE1_correlation_sweep.png")
    
    # Also create comparison figure with all 4 phases
    create_all_phases_comparison()

def create_all_phases_comparison():
    """Create comparison figure: Synthetic Sweep vs Real vs Zipfian"""
    
    # Load all results
    with open('results/PHASE1_correlation_sweep.json', 'r') as f:
        phase1 = json.load(f)
    with open('results/PHASE2_real_data_convergence.json', 'r') as f:
        phase2 = json.load(f)
    with open('results/PHASE4_zipfian_analysis.json', 'r') as f:
        phase4 = json.load(f)
    
    # Extract Phase 1 data
    hot_fractions = [r['hot_fraction'] for r in phase1['analysis']]
    synthetic_sens = [r['sensitivity_factor'] for r in phase1['analysis']]
    
    # Extract Phase 2 data (single point)
    real_sens = phase2['order_sensitivity_factor']
    
    # Extract Phase 4 data (single point)
    zipfian_sens = phase4['order_sensitivity_factor']
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # LEFT PANEL: Correlation sweep
    ax1.plot(hot_fractions, synthetic_sens, 'o-', linewidth=2.5, markersize=8, 
            color='#2E86AB', label='Synthetic (Parameterized Hot-Set)')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlabel('Hot-Set Fraction', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Order Sensitivity Factor', fontsize=12, fontweight='bold')
    ax1.set_title('PHASE 1: Correlation Sweep\n(Synthetic Data)', fontsize=13, fontweight='bold')
    ax1.set_xlim(0.15, 1.0)
    ax1.set_ylim(1.0, 5.5)
    ax1.legend(fontsize=11)
    
    # Add value labels
    for hf, sens in zip(hot_fractions, synthetic_sens):
        ax1.annotate(f'{sens:.2f}×', xy=(hf, sens), xytext=(0, 10), 
                   textcoords='offset points', ha='center', fontsize=9)
    
    # RIGHT PANEL: Distribution comparison
    distributions = ['Synthetic\n(80/20 Hot-Set)', 'Zipfian\n(Real Pattern)', 'Real URLs\n(Uniform)']
    sensitivities_comparison = [synthetic_sens[-1], zipfian_sens, real_sens]  # 0.8 hot-set = 4.85×
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    
    bars = ax2.bar(distributions, sensitivities_comparison, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, val in zip(bars, sensitivities_comparison):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}×', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('Order Sensitivity Factor', fontsize=12, fontweight='bold')
    ax2.set_title('Distribution Comparison\n(Phases 1, 2, 4)', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 5.5)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('plots/PHASE_comparison_all.png', dpi=300, bbox_inches='tight')
    print("✓ Comparison figure saved: plots/PHASE_comparison_all.png")

if __name__ == '__main__':
    plot_correlation_sweep()
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE: Correlation sweep and distribution comparison figures created")
    print("="*80)
