"""
Matplotlib Domain Adapter for DIX VISION Integration

This adapter translates Matplotlib visualization concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class MatplotlibDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for Matplotlib visualization data.
    
    This adapter handles:
    - Visualization concept mapping
    - Plot data transformation
    - Visual elements integration
    - Rendering results standardization
    - Visual enhancement
    """
    
    def __init__(self):
        super().__init__("matplotlib")
        
        # Matplotlib-specific concept mappings
        self.register_concept_mapping('plot', 'visual_representation')
        self.register_concept_mapping('figure', 'visual_canvas')
        self.register_concept_mapping('axis', 'dimension_scale')
        self.register_concept_mapping('legend', 'visual_key')
        self.register_concept_mapping('annotation', 'visual_commentary')
        
        # Plot type mappings
        self.plot_type_mappings = {
            'line': 'temporal_trend',
            'bar': 'comparative_magnitude',
            'scatter': 'relationship_plot',
            'histogram': 'distribution_analysis',
            'pie': 'proportional_visual',
            'box': 'statistical_summary'
        }
        
    def adapt_plot_data(self, plot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt Matplotlib plot data to DIX VISION format"""
        try:
            adapted = {
                'visual_representation': {
                    'representation_id': plot_data.get('plot_id', 'unknown'),
                    'plot_type': self.plot_type_mappings.get(plot_data.get('plot_type', 'unknown'), 'unknown_visual'),
                    'data_points': plot_data.get('data_points', 0),
                    'created_at': datetime.utcnow().isoformat()
                },
                'representation_metadata': {
                    'figure_size': plot_data.get('figure_size', []),
                    'axes': plot_data.get('axes', []),
                    'legend': plot_data.get('legend', {}),
                    'data_source': plot_data.get('data_source', 'unknown')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'visual_class': self._classify_visualization(plot_data),
                'complexity': self._assess_complexity(plot_data),
                'information_density': self._assess_information_density(plot_data),
                'analytical_value': self._assess_analytical_value(plot_data)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'matplotlib_plot',
                'source': 'matplotlib',
                'cognitive_layer': 'visualization'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt plot data: {str(e)}")
            raise
    
    def adapt_visualization_data(self, visualization: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt Matplotlib visualization data to DIX VISION format"""
        try:
            adapted = {
                'visual_canvas': {
                    'canvas_id': visualization.get('visualization_id', 'unknown'),
                    'dimensions': visualization.get('dimensions', []),
                    'dpi': visualization.get('dpi', 100),
                    'rendered_at': datetime.utcnow().isoformat()
                },
                'canvas_metadata': {
                    'format': visualization.get('format', 'png'),
                    'file_size': visualization.get('file_size', 0),
                    'color_space': visualization.get('color_space', 'RGB'),
                    'elements': visualization.get('elements', [])
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'visual_quality': self._assess_visual_quality(visualization),
                'rendering_efficiency': self._assess_rendering_efficiency(visualization),
                'cognitive_clarity': self._assess_cognitive_clarity(visualization),
                'visual_insight': self._extract_visual_insight(visualization)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'matplotlib_visualization',
                'source': 'matplotlib',
                'cognitive_layer': 'visual_rendering'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt visualization data: {str(e)}")
            raise
    
    def _classify_visualization(self, plot_data: Dict[str, Any]) -> str:
        """Classify the type of visualization"""
        plot_type = plot_data.get('plot_type', '').lower()
        data_points = plot_data.get('data_points', 0)
        
        if plot_type in ['line', 'scatter']:
            return 'temporal_analysis'
        elif plot_type == 'bar':
            return 'comparative_analysis'
        elif plot_type == 'histogram':
            return 'distribution_analysis'
        elif plot_type == 'pie':
            return 'proportional_analysis'
        elif data_points > 10000:
            return 'high_density_visualization'
        else:
            return 'standard_visualization'
    
    def _assess_complexity(self, plot_data: Dict[str, Any]) -> str:
        """Assess the complexity of the visualization"""
        data_points = plot_data.get('data_points', 0)
        axes_count = len(plot_data.get('axes', []))
        
        if data_points > 100000 or axes_count > 2:
            return 'high_complexity'
        elif data_points > 10000 or axes_count > 1:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_information_density(self, plot_data: Dict[str, Any]) -> str:
        """Assess the information density of the visualization"""
        data_points = plot_data.get('data_points', 0)
        figure_size = plot_data.get('figure_size', [10, 6])
        figure_area = figure_size[0] * figure_size[1] if len(figure_size) >= 2 else 60
        
        if figure_area > 0:
            density = data_points / figure_area
            if density > 1000:
                return 'high_density'
            elif density > 100:
                return 'moderate_density'
            else:
                return 'low_density'
        return 'unknown_density'
    
    def _assess_analytical_value(self, plot_data: Dict[str, Any]) -> str:
        """Assess the analytical value of the visualization"""
        plot_type = plot_data.get('plot_type', '').lower()
        
        if plot_type in ['scatter', 'line']:
            return 'pattern_analysis'
        elif plot_type == 'histogram':
            return 'distribution_analysis'
        elif plot_type == 'bar':
            return 'comparative_analysis'
        else:
            return 'general_visualization'
    
    def _assess_visual_quality(self, visualization: Dict[str, Any]) -> str:
        """Assess the visual quality of the rendering"""
        dpi = visualization.get('dpi', 100)
        format_type = visualization.get('format', 'png')
        
        if dpi >= 300 and format_type in ['svg', 'pdf']:
            return 'high_quality'
        elif dpi >= 150:
            return 'good_quality'
        elif dpi >= 100:
            return 'standard_quality'
        else:
            return 'basic_quality'
    
    def _assess_rendering_efficiency(self, visualization: Dict[str, Any]) -> str:
        """Assess the rendering efficiency"""
        file_size = visualization.get('file_size', 0)
        dimensions = visualization.get('dimensions', [])
        
        if dimensions and len(dimensions) >= 2:
            pixel_count = dimensions[0] * dimensions[1]
            if pixel_count > 0:
                bytes_per_pixel = file_size / pixel_count
                if bytes_per_pixel < 1:
                    return 'efficient'
                elif bytes_per_pixel < 4:
                    return 'standard'
                else:
                    return 'inefficient'
        return 'unknown_efficiency'
    
    def _assess_cognitive_clarity(self, visualization: Dict[str, Any]) -> str:
        """Assess the cognitive clarity of the visualization"""
        elements = visualization.get('elements', [])
        
        if len(elements) > 10:
            return 'complex_visual'
        elif len(elements) > 5:
            return 'moderate_visual'
        else:
            return 'clear_visual'
    
    def _extract_visual_insight(self, visualization: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual insight from the visualization"""
        format_type = visualization.get('format', 'png')
        
        return {
            'vector_capability': 'available' if format_type == 'svg' else 'limited',
            'print_suitability': 'high' if format_type in ['pdf', 'svg'] else 'standard',
            'web_optimization': 'standard' if format_type == 'png' else 'custom',
            'data_representation': 'visual_summary'
        }
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Matplotlib data"""
        if isinstance(data, dict):
            if 'plot_type' in data or 'data_points' in data:
                return self.adapt_plot_data(data)
            elif 'dimensions' in data or 'format' in data:
                return self.adapt_visualization_data(data)
        
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Matplotlib data"""
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        if target_format == DataFormat.JSON:
            return self._reverse_json_matplotlib_data(data)
        
        return data
    
    def _reverse_json_matplotlib_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Matplotlib data adaptation"""
        reverse_mappings = {v: k for k, v in self.concept_mappings.items()}
        adapted = {}
        
        for key, value in data.items():
            external_key = reverse_mappings.get(key, key)
            
            if isinstance(value, dict):
                adapted[external_key] = {reverse_mappings.get(k, k): v for k, v in value.items()}
            elif isinstance(value, list):
                adapted[external_key] = [
                    {reverse_mappings.get(k, k): v for k, v in item.items()} if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                adapted[external_key] = value
        
        return adapted


# Example usage
if __name__ == "__main__":
    adapter = MatplotlibDomainAdapter()
    
    sample_plot = {
        'plot_id': 'plot_12345',
        'plot_type': 'line',
        'data_points': 1000,
        'figure_size': [10, 6],
        'axes': ['x', 'y']
    }
    
    adapted_plot = adapter.adapt_plot_data(sample_plot)
    print("Adapted plot:", adapted_plot)
    
    print("Matplotlib Domain Adapter initialized successfully")
