# Research Paper Visualization Plan

## Overview
This document outlines the comprehensive visualization strategy for the "Stream Order Sensitivity in Distinct Element Estimation" research paper.

## Available Data Assets

### 1. **Real Data Convergence Analysis**
- **File**: `results/real_data_convergence_analysis_results.json` (33 KB)
- **Datasets**: 4 public datasets (Wikipedia, GitHub, Common Crawl, Enron)
- **Orderings**: 3 per dataset (grouped/sorted, random, chronological)
- **Metrics**: 20 convergence checkpoints per experiment, final error, time-to-5% convergence
- **Key Finding**: Sensitivity ranges from 1.0× to 1.583× across datasets

### 2. **Synthetic Correlation Analysis**
- **File**: `results/synthetic_correlation_analysis_results.json`
- **Experiments**: Hot-set fraction parameterization (0.2-0.95)
- **Metrics**: Sensitivity factor vs correlation level
- **Key Finding**: Sensitivity increases with data correlation

### 3. **Zipfian Distribution Analysis**
- **File**: `results/zipfian_distribution_analysis_results.json`
- **Source**: Common Crawl domains (realistic Zipfian distribution)
- **Purpose**: Validate findings on real-world skewed distributions

## Proposed Visualizations (15+ plots)

### **Section 1: Real Data Analysis** (6 plots)

1. **Convergence Curves by Dataset** (line plot)
   - X-axis: Stream progression (%)
   - Y-axis: Relative error (%)
   - Lines: One per dataset
   - Shows how different datasets achieve convergence at different rates

2. **Order Sensitivity Comparison** (bar chart)
   - X-axis: Dataset names
   - Y-axis: Sensitivity factor
   - Bars: Grouped, Random, Chrono (if multiple orderings available)
   - Highlights which datasets are most sensitive to stream order

3. **Duplicate Ratio vs Sensitivity** (scatter plot)
   - X-axis: Duplicate ratio (%)
   - Y-axis: Sensitivity factor
   - Points: One per dataset
   - Shows correlation between data duplication and order sensitivity

4. **Convergence Speed Heatmap** (time-to-5% error across datasets and orderings)
   - Rows: Datasets
   - Columns: Stream orderings
   - Color intensity: Time to reach 5% error
   - Visualizes where order matters most

5. **Final Error by Dataset** (grouped bar chart)
   - X-axis: Dataset
   - Y-axis: Final relative error (%)
   - Grouped by ordering type
   - Shows estimation quality differences

6. **Data Characteristics Table/Chart** (multi-metric comparison)
   - Metrics: Total items, unique items, duplicate %, sensitivity
   - Format: Heatmap or detailed table visualization
   - Context: Understand data properties affecting sensitivity

### **Section 2: Synthetic Data Analysis** (4 plots)

7. **Sensitivity vs Data Correlation** (existing - refine)
   - Already created: `plots/synthetic_correlation_analysis.png`
   - Enhance with: confidence intervals, reference points

8. **Sensitivity Progression** (line plot)
   - X-axis: Hot-set fraction
   - Y-axis: Sensitivity factor
   - Multiple lines: Different stream sizes
   - Shows how sensitivity scales with correlation level

9. **Convergence Comparison: Grouped vs Random** (dual line plot)
   - X-axis: Stream progression
   - Y-axis: Relative error
   - Lines: Grouped ordering vs Random ordering
   - Emphasis: Gap between orderings

10. **Synthetic vs Real Data Overlay** (comparison scatter)
    - X-axis: Data correlation/characteristic
    - Y-axis: Sensitivity factor
    - Points: Synthetic experiments and real datasets
    - Shows validation of synthetic model against real data

### **Section 3: Distribution Analysis** (3 plots)

11. **Zipfian Sensitivity Analysis** (bar chart)
    - Sensitivity factors for Zipfian-distributed data
    - Compare with uniform and real distributions

12. **Distribution Pattern Comparison** (histogram overlay)
    - Distribution of item frequencies
    - Overlay: Synthetic, Zipfian, real data samples

13. **Duplicate Pattern Analysis** (line plot)
    - Cumulative unique items vs stream position
    - Multiple lines: Different distributions
    - Shows duplicate accumulation patterns

### **Section 4: Cross-Experiment Analysis** (3+ plots)

14. **Sensitivity Heatmap: All Dimensions** (2D heatmap)
    - Rows: Datasets (including synthetic)
    - Columns: Data characteristics (correlation/skew level)
    - Color: Sensitivity factor
    - Comprehensive sensitivity landscape

15. **Error Stability Across Orders** (multi-panel)
    - Subplots: One per dataset
    - Each shows: Error variance by ordering type
    - Metric: Error standard deviation at convergence

16. **Efficiency Comparison** (multi-metric visualization)
    - Metrics: Time-to-convergence, memory usage (implicit from algorithm)
    - Compare orderings: Grouped vs Random vs Chrono

### **Section 5: Summary & Tables** (2+ visualizations)

17. **Key Metrics Summary Table** (publication-quality table)
    - Columns: Dataset, Unique Items, Dup%, Sensitivity, Time-to-5%-Error
    - Rows: All datasets
    - Format: High-contrast, easy to read

18. **Main Findings Infographic** (visual summary)
    - Key takeaways: Max sensitivity (Enron 1.583×), min sensitivity (Wikipedia, CC 1.0×)
    - Correlation: Duplicate % positively correlates with sensitivity
    - Recommendation: Sort data when distribution is skewed

## Implementation Priority

### **High Priority (Must Have)**
- [x] Convergence curves by dataset
- [x] Order sensitivity comparison bar chart
- [x] Duplicate ratio vs sensitivity scatter
- [ ] Sensitivity heatmap (datasets × orderings)
- [ ] Key metrics summary table
- [ ] Synthetic correlation plot (already done)

### **Medium Priority (Should Have)**
- [ ] Convergence speed comparison
- [ ] Data characteristics table
- [ ] Distribution pattern analysis
- [ ] Error stability comparison
- [ ] Synthetic vs real overlay

### **Low Priority (Nice to Have)**
- [ ] Zipfian detailed analysis
- [ ] Efficiency comparison charts
- [ ] Main findings infographic

## Technical Details

**Plot Generation Scripts**:
- `plot_real_data_convergence.py` - Generate convergence and sensitivity plots
- `plot_synthetic_analysis.py` - Enhance synthetic correlation analysis
- `plot_summary_comparisons.py` - Cross-experiment comparison plots
- `plot_metrics_table.py` - Summary table visualization

**Output Specifications**:
- Format: PNG (publication-quality)
- DPI: 300 (high resolution for printing)
- Size: 10×6 inches (or multi-panel as appropriate)
- Colors: Publication-friendly palette (blues, greens, minimal red)
- Fonts: Sans-serif, 11-12 pt for readability

**Data Pipeline**:
1. Load JSON result files
2. Extract key metrics
3. Generate visualizations
4. Save as PNG at 300 DPI
5. Commit to Git with documentation

## Expected Paper Sections Using Visualizations

1. **Introduction**: Main findings infographic
2. **Related Work**: Distribution comparison
3. **Methodology**: Algorithm overview (not visualized)
4. **Results**:
   - Real data convergence curves
   - Sensitivity comparison across datasets
   - Relationship between data characteristics and sensitivity
5. **Synthetic Validation**: Correlation sweep analysis
6. **Discussion**: Cross-experiment summary heatmap
7. **Conclusion**: Key metrics table

## Notes for Author

- Use consistent color scheme across all plots
- Ensure accessibility (colorblind-friendly palette)
- Include proper axis labels, legends, and figure captions
- High-resolution (300 DPI) essential for conference/journal publication
- Consider dark mode readability if presenting digitally
- Each plot should tell a clear story about order sensitivity

