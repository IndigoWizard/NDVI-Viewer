"""NDVI Statistics and Data Profiling Module

This module provides functions for analyzing NDVI data including:
- Area calculations in different units
- Vegetation coverage statistics  
- NDVI class distribution analysis
- Statistical profiling and reporting
"""

import numpy as np
import ee
import pandas as pd
from typing import Dict, Tuple, List

# Constants for area conversions
SQUARE_METERS_TO_HECTARES = 1 / 10000
SQUARE_METERS_TO_ACRES = 0.000247105
SQUARE_METERS_TO_SQ_KM = 1 / 1000000
SQUARE_METERS_TO_SQ_MI = 0.000000386102

# NDVI Classification thresholds
NDVI_CLASSES = {
    'Absent Vegetation': (0, 0.15),
    'Bare Soil': (0.15, 0.25),
    'Low Vegetation': (0.25, 0.35),
    'Light Vegetation': (0.35, 0.45),
    'Moderate Vegetation': (0.45, 0.65),
    'Strong Vegetation': (0.65, 0.75),
    'Dense Vegetation': (0.75, 1.0)
}

VEGETATION_THRESHOLD = 0.3  # NDVI threshold for vegetation coverage

class NDVIStatistics:
    """Class for calculating NDVI statistics and area metrics"""
    
    def __init__(self, geometry_aoi):
        """
        Initialize with Area of Interest geometry
        
        Args:
            geometry_aoi: Earth Engine Geometry object
        """
        self.geometry_aoi = geometry_aoi
        self.pixel_scale = 10  # Sentinel-2 pixel scale in meters
        
    def get_total_area_metrics(self) -> Dict[str, float]:
        """
        Calculate total area of interest in different units
        
        Returns:
            Dictionary with area measurements in different units
        """
        # Calculate area in square meters
        area_sq_m = self.geometry_aoi.area(maxError=1).getInfo()
        
        return {
            'square_meters': area_sq_m,
            'hectares': area_sq_m * SQUARE_METERS_TO_HECTARES,
            'acres': area_sq_m * SQUARE_METERS_TO_ACRES,
            'square_kilometers': area_sq_m * SQUARE_METERS_TO_SQ_KM,
            'square_miles': area_sq_m * SQUARE_METERS_TO_SQ_MI
        }
    
    def get_vegetation_coverage(self, ndvi_image) -> Dict[str, float]:
        """
        Calculate vegetation coverage statistics
        
        Args:
            ndvi_image: Earth Engine NDVI image
            
        Returns:
            Dictionary with vegetation coverage metrics
        """
        # Create vegetation mask (NDVI > threshold)
        vegetation_mask = ndvi_image.gte(VEGETATION_THRESHOLD)
        
        # Calculate pixel counts
        total_pixels = ndvi_image.select('nd').reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo()
        
        vegetation_pixels = vegetation_mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo()
        
        total_count = total_pixels.get('nd', 0)
        veg_count = vegetation_pixels.get('nd', 0)
        
        # Calculate areas
        pixel_area = self.pixel_scale ** 2  # area per pixel in square meters
        total_area = total_count * pixel_area
        vegetation_area = veg_count * pixel_area
        
        return {
            'total_area_sq_m': total_area,
            'vegetation_area_sq_m': vegetation_area,
            'vegetation_percentage': (vegetation_area / total_area * 100) if total_area > 0 else 0,
            'non_vegetation_area_sq_m': total_area - vegetation_area,
            'non_vegetation_percentage': ((total_area - vegetation_area) / total_area * 100) if total_area > 0 else 0
        }
    
    def get_ndvi_class_distribution(self, ndvi_image) -> Dict[str, Dict[str, float]]:
        """
        Calculate area distribution for each NDVI class
        
        Args:
            ndvi_image: Earth Engine NDVI image
            
        Returns:
            Dictionary with class distribution metrics
        """
        class_stats = {}
        total_area_stats = self.get_total_area_metrics()
        total_area = total_area_stats['square_meters']
        
        for class_name, (min_val, max_val) in NDVI_CLASSES.items():
            # Create mask for this class
            class_mask = ndvi_image.gte(min_val).And(ndvi_image.lt(max_val))
            
            # Calculate pixel count for this class
            class_pixels = class_mask.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=self.geometry_aoi,
                scale=self.pixel_scale,
                maxPixels=1e9
            ).getInfo()
            
            pixel_count = class_pixels.get('nd', 0)
            class_area = pixel_count * (self.pixel_scale ** 2)
            percentage = (class_area / total_area * 100) if total_area > 0 else 0
            
            class_stats[class_name] = {
                'area_sq_m': class_area,
                'area_hectares': class_area * SQUARE_METERS_TO_HECTARES,
                'area_acres': class_area * SQUARE_METERS_TO_ACRES,
                'percentage': percentage,
                'pixel_count': pixel_count,
                'ndvi_range': f'{min_val:.2f} - {max_val:.2f}'
            }
        
        return class_stats
    
    def get_ndvi_summary_statistics(self, ndvi_image) -> Dict[str, float]:
        """
        Calculate summary statistics for NDVI values
        
        Args:
            ndvi_image: Earth Engine NDVI image
            
        Returns:
            Dictionary with summary statistics
        """
        # Calculate statistics using Earth Engine reducers
        stats = ndvi_image.reduceRegion(
            reducer=ee.Reducer.minMax().combine(
                ee.Reducer.mean(), sharedInputs=True
            ).combine(
                ee.Reducer.stdDev(), sharedInputs=True
            ).combine(
                ee.Reducer.percentile([25, 50, 75]), sharedInputs=True
            ),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo()
        
        return {
            'min': stats.get('nd_min', 0),
            'max': stats.get('nd_max', 0),
            'mean': stats.get('nd_mean', 0),
            'std_dev': stats.get('nd_stdDev', 0),
            'percentile_25': stats.get('nd_p25', 0),
            'median': stats.get('nd_p50', 0),
            'percentile_75': stats.get('nd_p75', 0)
        }
    
    def calculate_change_statistics(self, initial_ndvi, updated_ndvi) -> Dict[str, any]:
        """
        Calculate change statistics between two NDVI images
        
        Args:
            initial_ndvi: Initial NDVI image
            updated_ndvi: Updated NDVI image
            
        Returns:
            Dictionary with change statistics
        """
        # Calculate difference image
        ndvi_change = updated_ndvi.subtract(initial_ndvi)
        
        # Get statistics for change image
        change_stats = ndvi_change.reduceRegion(
            reducer=ee.Reducer.minMax().combine(
                ee.Reducer.mean(), sharedInputs=True
            ).combine(
                ee.Reducer.stdDev(), sharedInputs=True
            ),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo()
        
        # Calculate areas of improvement/degradation
        improvement_mask = ndvi_change.gt(0.1)  # Significant improvement
        degradation_mask = ndvi_change.lt(-0.1)  # Significant degradation
        stable_mask = ndvi_change.gte(-0.1).And(ndvi_change.lte(0.1))  # Stable
        
        # Get pixel counts for each category
        improvement_pixels = improvement_mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo().get('nd', 0)
        
        degradation_pixels = degradation_mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo().get('nd', 0)
        
        stable_pixels = stable_mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=self.geometry_aoi,
            scale=self.pixel_scale,
            maxPixels=1e9
        ).getInfo().get('nd', 0)
        
        # Calculate areas
        pixel_area = self.pixel_scale ** 2
        total_area = self.get_total_area_metrics()['square_meters']
        
        return {
            'change_statistics': {
                'min_change': change_stats.get('nd_min', 0),
                'max_change': change_stats.get('nd_max', 0),
                'mean_change': change_stats.get('nd_mean', 0),
                'std_dev_change': change_stats.get('nd_stdDev', 0)
            },
            'change_categories': {
                'improvement': {
                    'area_sq_m': improvement_pixels * pixel_area,
                    'percentage': (improvement_pixels * pixel_area / total_area * 100) if total_area > 0 else 0,
                    'description': 'Areas with NDVI increase > 0.1'
                },
                'degradation': {
                    'area_sq_m': degradation_pixels * pixel_area,
                    'percentage': (degradation_pixels * pixel_area / total_area * 100) if total_area > 0 else 0,
                    'description': 'Areas with NDVI decrease > 0.1'
                },
                'stable': {
                    'area_sq_m': stable_pixels * pixel_area,
                    'percentage': (stable_pixels * pixel_area / total_area * 100) if total_area > 0 else 0,
                    'description': 'Areas with NDVI change between -0.1 and 0.1'
                }
            }
        }
    
    def generate_comprehensive_report(self, initial_ndvi, updated_ndvi=None) -> Dict[str, any]:
        """
        Generate comprehensive statistics report
        
        Args:
            initial_ndvi: Initial NDVI image
            updated_ndvi: Optional updated NDVI image for comparison
            
        Returns:
            Complete statistics report dictionary
        """
        report = {
            'area_metrics': self.get_total_area_metrics(),
            'initial_ndvi_stats': {
                'summary_statistics': self.get_ndvi_summary_statistics(initial_ndvi),
                'vegetation_coverage': self.get_vegetation_coverage(initial_ndvi),
                'class_distribution': self.get_ndvi_class_distribution(initial_ndvi)
            }
        }
        
        if updated_ndvi is not None:
            report['updated_ndvi_stats'] = {
                'summary_statistics': self.get_ndvi_summary_statistics(updated_ndvi),
                'vegetation_coverage': self.get_vegetation_coverage(updated_ndvi),
                'class_distribution': self.get_ndvi_class_distribution(updated_ndvi)
            }
            report['change_analysis'] = self.calculate_change_statistics(initial_ndvi, updated_ndvi)
        
        return report

def format_area_display(area_sq_m: float) -> str:
    """
    Format area for display with appropriate units
    
    Args:
        area_sq_m: Area in square meters
        
    Returns:
        Formatted string with appropriate units
    """
    if area_sq_m < 10000:  # Less than 1 hectare
        return f"{area_sq_m:.1f} m²"
    elif area_sq_m < 1000000:  # Less than 1 km²
        return f"{area_sq_m * SQUARE_METERS_TO_HECTARES:.2f} hectares"
    else:
        return f"{area_sq_m * SQUARE_METERS_TO_SQ_KM:.2f} km²"

def get_vegetation_health_description(mean_ndvi: float) -> str:
    """
    Get vegetation health description based on mean NDVI
    
    Args:
        mean_ndvi: Mean NDVI value
        
    Returns:
        Health description string
    """
    if mean_ndvi < 0.2:
        return "Poor - Mostly non-vegetated surfaces"
    elif mean_ndvi < 0.4:
        return "Fair - Sparse vegetation"
    elif mean_ndvi < 0.6:
        return "Good - Moderate vegetation density"
    elif mean_ndvi < 0.8:
        return "Very Good - Dense, healthy vegetation"
    else:
        return "Excellent - Very dense, healthy vegetation"    
