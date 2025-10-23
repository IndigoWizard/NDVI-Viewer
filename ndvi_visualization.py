"""NDVI Visualization Module

This module provides visualization functions for NDVI statistics including:
- Bar charts for class distribution
- Pie charts for vegetation coverage
- Comparison charts for baseline vs updated NDVI
- Summary statistics displays
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io
import base64

# Color schemes for visualizations
NDVI_CLASS_COLORS = [
    '#a50026',  # Absent Vegetation
    '#ed5e3d',  # Bare Soil
    '#f9f7ae',  # Low Vegetation
    '#f4ff78',  # Light Vegetation
    '#9ed569',  # Moderate Vegetation
    '#229b51',  # Strong Vegetation
    '#006837'   # Dense Vegetation
]

class NDVIVisualizer:
    """Class for creating NDVI data visualizations"""
    
    def __init__(self, color_palette='Normal'):
        """
        Initialize visualizer with color palette
        
        Args:
            color_palette: Color palette name for accessibility
        """
        self.color_palette = color_palette
        self.colors = self._get_color_scheme(color_palette)
    
    def _get_color_scheme(self, palette_name):
        """Get appropriate color scheme based on accessibility needs"""
        if palette_name == 'Deuteranopia':
            return ['#95a600', '#92ed3e', '#affac5', '#78ffb0', '#69d6c6', '#22459c', '#000e69']
        elif palette_name == 'Protanopia':
            return ['#95a600', '#92ed3e', '#affac5', '#78ffb0', '#69d6c6', '#22459c', '#000e69']
        elif palette_name == 'Tritanopia':
            return ['#ed4700', '#ed8a00', '#e1fabe', '#99ff94', '#87bede', '#2e40cf', '#0600bc']
        elif palette_name == 'Achromatopsia':
            return ['#004f3d', '#338796', '#66a4f5', '#3683ff', '#3d50ca', '#421c7f', '#290058']
        else:
            return NDVI_CLASS_COLORS
    
    def create_class_distribution_chart(self, class_stats: Dict, title: str = "NDVI Class Distribution"):
        """
        Create bar chart showing NDVI class distribution
        
        Args:
            class_stats: Dictionary with class distribution data
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        classes = list(class_stats.keys())
        percentages = [stats['percentage'] for stats in class_stats.values()]
        areas_ha = [stats['area_hectares'] for stats in class_stats.values()]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=classes,
            y=percentages,
            text=[f"{p:.1f}%<br>{a:.2f} ha" for p, a in zip(percentages, areas_ha)],
            textposition='outside',
            marker_color=self.colors,
            hovertemplate='<b>%{x}</b><br>Percentage: %{y:.2f}%<br>Area: %{customdata:.2f} ha<extra></extra>',
            customdata=areas_ha
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="NDVI Class",
            yaxis_title="Percentage of Total Area (%)",
            xaxis_tickangle=-45,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_vegetation_pie_chart(self, vegetation_stats: Dict):
        """
        Create pie chart for vegetation vs non-vegetation coverage
        
        Args:
            vegetation_stats: Dictionary with vegetation coverage data
            
        Returns:
            Plotly figure object
        """
        labels = ['Vegetation', 'Non-Vegetation']
        values = [
            vegetation_stats['vegetation_percentage'],
            vegetation_stats['non_vegetation_percentage']
        ]
        colors = ['#4CAF50', '#FF9800']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=colors,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>%{percent}<br>Area: %{customdata:.2f} m²<extra></extra>',
            customdata=[vegetation_stats['vegetation_area_sq_m'], vegetation_stats['non_vegetation_area_sq_m']]
        )])
        
        fig.update_layout(
            title="Vegetation Coverage Distribution",
            height=400
        )
        
        return fig
    
    def create_comparison_chart(self, initial_stats: Dict, updated_stats: Dict):
        """
        Create side-by-side comparison of initial and updated NDVI
        
        Args:
            initial_stats: Initial NDVI class distribution
            updated_stats: Updated NDVI class distribution
            
        Returns:
            Plotly figure object
        """
        classes = list(initial_stats.keys())
        initial_pct = [stats['percentage'] for stats in initial_stats.values()]
        updated_pct = [stats['percentage'] for stats in updated_stats.values()]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Initial',
            x=classes,
            y=initial_pct,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Updated',
            x=classes,
            y=updated_pct,
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title="NDVI Class Distribution Comparison",
            xaxis_title="NDVI Class",
            yaxis_title="Percentage of Total Area (%)",
            xaxis_tickangle=-45,
            barmode='group',
            height=500,
            legend=dict(x=0.8, y=1.0)
        )
        
        return fig
    
    def create_change_detection_chart(self, change_stats: Dict):
        """
        Create chart showing areas of improvement, degradation, and stability
        
        Args:
            change_stats: Dictionary with change detection data
            
        Returns:
            Plotly figure object
        """
        categories = list(change_stats['change_categories'].keys())
        percentages = [stats['percentage'] for stats in change_stats['change_categories'].values()]
        areas = [stats['area_sq_m'] / 10000 for stats in change_stats['change_categories'].values()]  # Convert to hectares
        colors_map = {'improvement': '#4CAF50', 'stable': '#FFC107', 'degradation': '#F44336'}
        colors = [colors_map[cat] for cat in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[cat.capitalize() for cat in categories],
            y=percentages,
            text=[f"{p:.1f}%<br>{a:.2f} ha" for p, a in zip(percentages, areas)],
            textposition='outside',
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Percentage: %{y:.2f}%<br>Area: %{customdata:.2f} ha<extra></extra>',
            customdata=areas
        ))
        
        fig.update_layout(
            title="NDVI Change Detection Analysis",
            xaxis_title="Change Category",
            yaxis_title="Percentage of Total Area (%)",
            height=450,
            showlegend=False
        )
        
        return fig
    
    def create_statistics_table(self, summary_stats: Dict):
        """
        Create formatted table for summary statistics
        
        Args:
            summary_stats: Dictionary with summary statistics
            
        Returns:
            Plotly table figure
        """
        stats_df = pd.DataFrame([
            ['Minimum', f"{summary_stats['min']:.4f}"],
            ['Maximum', f"{summary_stats['max']:.4f}"],
            ['Mean', f"{summary_stats['mean']:.4f}"],
            ['Median', f"{summary_stats['median']:.4f}"],
            ['Std Dev', f"{summary_stats['std_dev']:.4f}"],
            ['25th Percentile', f"{summary_stats['percentile_25']:.4f}"],
            ['75th Percentile', f"{summary_stats['percentile_75']:.4f}"]
        ], columns=['Statistic', 'Value'])
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Statistic</b>', '<b>Value</b>'],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[stats_df['Statistic'], stats_df['Value']],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )
        )])
        
        fig.update_layout(
            title="NDVI Summary Statistics",
            height=350
        )
        
        return fig

def create_matplotlib_class_chart(class_stats: Dict, colors: List = None):
    """
    Create matplotlib bar chart for class distribution (for PDF export)
    
    Args:
        class_stats: Dictionary with class distribution data
        colors: Optional list of colors
        
    Returns:
        Matplotlib figure object
    """
    if colors is None:
        colors = NDVI_CLASS_COLORS
    
    classes = list(class_stats.keys())
    percentages = [stats['percentage'] for stats in class_stats.values()]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(classes, percentages, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('NDVI Class', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Total Area (%)', fontsize=12, fontweight='bold')
    ax.set_title('NDVI Class Distribution', fontsize=14, fontweight='bold')
    ax.set_xticklabels(classes, rotation=45, ha='right')
    
    # Add percentage labels on bars
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig

def fig_to_base64(fig):
    """
    Convert matplotlib figure to base64 string for embedding
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        Base64 encoded string
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64
