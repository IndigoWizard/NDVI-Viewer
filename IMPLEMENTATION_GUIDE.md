# NDVI Data Profiling and Stats - Implementation Guide

## Overview
This guide provides complete implementation instructions for the "Data Profiling and Stats" feature (Issue #25) for the NDVI-Viewer application.

## Files Created

### 1. `ndvi_statistics.py` ✅ 
**Status:** Completed and committed  
**Purpose:** Core statistics engine for NDVI data analysis

**Key Features:**
- Area calculations in multiple units (m², hectares, acres, km², mi²)
- Vegetation coverage statistics
- NDVI class distribution across 7 classes
- Summary statistics (min, max, mean, median, std dev, percentiles)
- Change detection between two NDVI images
- Comprehensive report generation

### 2. `ndvi_visualization.py` ✅
**Status:** Completed and committed  
**Purpose:** Visualization functions for NDVI statistics

**Key Features:**
- Bar charts for class distribution
- Pie charts for vegetation coverage
- Comparison charts for baseline vs updated NDVI
- Change detection visualizations
- Summary statistics tables
- Matplotlib charts for PDF export
- Accessibility support with multiple color palettes

## Remaining Implementation Steps

### Step 1: Update `requirements.txt`
Add these dependencies to the existing requirements.txt file:

```
matplotlib==3.7.1
plotly==5.14.1
pandas==2.0.3
numpy==1.24.3
fpdf2==2.7.4
kaleido==0.2.1
```

### Step 2: Create `pdf_generator.py`
Create a new file with PDF report generation capabilities:

```python
from fpdf import FPDF
from datetime import datetime
import ndvi_statistics as ndvi_stats
import ndvi_visualization as ndvi_viz
import matplotlib.pyplot as plt

class NDVIReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'NDVI Analysis Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(report_data, output_path='ndvi_report.pdf'):
    pdf = NDVIReport()
    pdf.add_page()
    
    # Add report title and date
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(10)
    
    # Add area metrics section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Area Metrics', 0, 1)
    pdf.set_font('Arial', '', 11)
    area_metrics = report_data['area_metrics']
    pdf.cell(0, 8, f"Total Area: {area_metrics['square_meters']:.2f} m²", 0, 1)
    pdf.cell(0, 8, f"           {area_metrics['hectares']:.4f} hectares", 0, 1)
    pdf.cell(0, 8, f"           {area_metrics['acres']:.4f} acres", 0, 1)
    pdf.ln(5)
    
    # Add statistics tables
    # Add charts (convert Plotly to images)
    
    pdf.output(output_path)
    return output_path
```

### Step 3: Update `app.py` - Add Statistics Section

Add the following imports at the top of `app.py`:

```python
from ndvi_statistics import NDVIStatistics, format_area_display, get_vegetation_health_description
from ndvi_visualization import NDVIVisualizer
import plotly.io as pio
```

Add this code after the map section in `app.py`, inside the `main()` function:

```python
# Data Profiling and Stats Section
if submitted and geometry_aoi:
    st.markdown("---")
    st.header("📊 Data Profiling & Statistics")
    
    # Initialize statistics calculator
    stats_calculator = NDVIStatistics(geometry_aoi)
    visualizer = NDVIVisualizer(color_palette=accessibility)
    
    # User options for statistics
    with st.expander("📈 Statistics Options", expanded=True):
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        show_area = col_opt1.checkbox("Show Area Metrics", value=True)
        show_veg_coverage = col_opt2.checkbox("Show Vegetation Coverage", value=True)
        show_class_dist = col_opt3.checkbox("Show Class Distribution", value=True)
        show_summary_stats = col_opt1.checkbox("Show Summary Statistics", value=True)
        show_comparison = col_opt2.checkbox("Show Comparison Charts", value=(initial_date != updated_date))
        generate_pdf_btn = col_opt3.button("📄 Generate PDF Report")
    
    # Calculate statistics
    try:
        # Area Metrics
        if show_area:
            st.subheader("📏 Area of Interest Metrics")
            area_metrics = stats_calculator.get_total_area_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Square Meters", f"{area_metrics['square_meters']:.2f} m²")
            col2.metric("Hectares", f"{area_metrics['hectares']:.4f} ha")
            col3.metric("Acres", f"{area_metrics['acres']:.4f} ac")
            col4.metric("Square Kilometers", f"{area_metrics['square_kilometers']:.6f} km²")
        
        # Vegetation Coverage
        if show_veg_coverage:
            st.subheader("🌿 Vegetation Coverage Analysis")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                veg_coverage = stats_calculator.get_vegetation_coverage(updated_ndvi)
                st.metric("Vegetation Area", format_area_display(veg_coverage['vegetation_area_sq_m']))
                st.metric("Vegetation %", f"{veg_coverage['vegetation_percentage']:.2f}%")
                st.metric("Non-Vegetation %", f"{veg_coverage['non_vegetation_percentage']:.2f}%")
            
            with col2:
                pie_chart = visualizer.create_vegetation_pie_chart(veg_coverage)
                st.plotly_chart(pie_chart, use_container_width=True)
        
        # NDVI Class Distribution
        if show_class_dist:
            st.subheader("📊 NDVI Class Distribution")
            
            class_dist = stats_calculator.get_ndvi_class_distribution(updated_ndvi)
            
            # Display as chart
            bar_chart = visualizer.create_class_distribution_chart(class_dist)
            st.plotly_chart(bar_chart, use_container_width=True)
            
            # Display as table
            import pandas as pd
            df = pd.DataFrame([
                {
                    'Class': class_name,
                    'NDVI Range': stats['ndvi_range'],
                    'Area (ha)': f"{stats['area_hectares']:.2f}",
                    'Percentage': f"{stats['percentage']:.2f}%"
                }
                for class_name, stats in class_dist.items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary Statistics
        if show_summary_stats:
            st.subheader("📈 Summary Statistics")
            
            summary_stats = stats_calculator.get_ndvi_summary_statistics(updated_ndvi)
            health_desc = get_vegetation_health_description(summary_stats['mean'])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean NDVI", f"{summary_stats['mean']:.4f}")
            col2.metric("Median NDVI", f"{summary_stats['median']:.4f}")
            col3.metric("Min NDVI", f"{summary_stats['min']:.4f}")
            col4.metric("Max NDVI", f"{summary_stats['max']:.4f}")
            
            st.info(f"**Vegetation Health Assessment:** {health_desc}")
            
            # Statistics table
            stats_table = visualizer.create_statistics_table(summary_stats)
            st.plotly_chart(stats_table, use_container_width=True)
        
        # Comparison (if dates are different)
        if show_comparison and initial_date != updated_date:
            st.subheader("🔄 Temporal Comparison Analysis")
            
            initial_class_dist = stats_calculator.get_ndvi_class_distribution(initial_ndvi)
            updated_class_dist = stats_calculator.get_ndvi_class_distribution(updated_ndvi)
            
            # Comparison chart
            comparison_chart = visualizer.create_comparison_chart(initial_class_dist, updated_class_dist)
            st.plotly_chart(comparison_chart, use_container_width=True)
            
            # Change detection
            st.subheader("🔍 Change Detection")
            change_stats = stats_calculator.calculate_change_statistics(initial_ndvi, updated_ndvi)
            
            col1, col2, col3 = st.columns(3)
            improvement = change_stats['change_categories']['improvement']
            degradation = change_stats['change_categories']['degradation']
            stable = change_stats['change_categories']['stable']
            
            col1.metric("🟢 Improvement", f"{improvement['percentage']:.2f}%",
                       delta=f"{format_area_display(improvement['area_sq_m'])}")
            col2.metric("🔴 Degradation", f"{degradation['percentage']:.2f}%",
                       delta=f"{format_area_display(degradation['area_sq_m'])}", delta_color="inverse")
            col3.metric("🟡 Stable", f"{stable['percentage']:.2f}%",
                       delta=f"{format_area_display(stable['area_sq_m'])}")
            
            # Change detection chart
            change_chart = visualizer.create_change_detection_chart(change_stats)
            st.plotly_chart(change_chart, use_container_width=True)
        
        # PDF Generation
        if generate_pdf_btn:
            st.info("📄 PDF generation feature requires additional implementation. See IMPLEMENTATION_GUIDE.md for details.")
            
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")
        st.exception(e)
```

## Testing Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app locally:**
   ```bash
   streamlit run app.py
   ```

3. **Test features:**
   - Upload a GeoJSON file
   - Select dates
   - Generate map
   - View statistics section
   - Toggle different stat options
   - Test with different dates for comparison

## Feature Checklist

✅ Size of area of interest in different metrics  
✅ Area surface covered by vegetation  
✅ Area surface of each class of NDVI values  
✅ Percentage of each NDVI class compared to total area  
✅ Charts comparing baseline NDVI and updated NDVI values  
⚠️  PDF report generation (requires Step 2 implementation)

## Notes

- The implementation uses Earth Engine's `reduceRegion` for calculations
- All statistics are calculated server-side via Earth Engine API
- Visualizations use Plotly for interactive charts
- Accessibility features include multiple color palettes
- The system handles both single-date and comparison scenarios

## Contributing

To complete this feature:
1. Implement the PDF generator module
2. Test all statistics calculations
3. Verify accessibility features
4. Add error handling for edge cases
5. Document any limitations

## References

- Issue #25: https://github.com/IndigoWizard/NDVI-Viewer/issues/25
- Earth Engine Documentation: https://developers.google.com/earth-engine
- Streamlit Documentation: https://docs.streamlit.io
