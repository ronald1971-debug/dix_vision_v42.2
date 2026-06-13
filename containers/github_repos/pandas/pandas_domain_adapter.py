"""
Pandas Domain Adapter for DIX VISION Integration

This adapter translates Pandas data analysis concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from base_domain_adapter import (
    SystemDomainAdapter,
    DomainType,
    DataFormat
)

class PandasDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for Pandas data analysis data.
    
    This adapter handles:
    - Data analysis concept mapping
    - DataFrame data transformation
    - Data operations integration
    - Analysis results standardization
    - Data enhancement
    """
    
    def __init__(self):
        super().__init__("pandas")
        
        # Pandas-specific concept mappings
        self.register_concept_mapping('dataframe', 'data_matrix')
        self.register_concept_mapping('series', 'data_vector')
        self.register_concept_mapping('index', 'data_key')
        self.register_concept_mapping('column', 'data_attribute')
        self.register_concept_mapping('analysis', 'data_insight')
        
        # Data type mappings
        self.dtype_mappings = {
            'float64': 'high_precision_decimal',
            'float32': 'standard_decimal',
            'int64': 'large_integer',
            'int32': 'standard_integer',
            'object': 'text_data',
            'bool': 'logical_value',
            'datetime64': 'temporal_data',
            'category': 'categorical_data'
        }
        
    def adapt_dataframe_data(self, dataframe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt Pandas DataFrame data to DIX VISION format"""
        try:
            adapted = {
                'data_matrix': {
                    'matrix_id': dataframe_data.get('dataframe_id', 'unknown'),
                    'shape': dataframe_data.get('shape', []),
                    'row_count': dataframe_data.get('shape', [0, 0])[0],
                    'column_count': dataframe_data.get('shape', [0, 0])[1],
                    'created_at': datetime.utcnow().isoformat()
                },
                'matrix_metadata': {
                    'columns': dataframe_data.get('columns', []),
                    'dtypes': dataframe_data.get('dtypes', {}),
                    'index_range': dataframe_data.get('index_range', []),
                    'memory_usage': dataframe_data.get('memory_usage', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'matrix_class': self._classify_dataframe(dataframe_data),
                'complexity': self._assess_complexity(dataframe_data),
                'data_quality': self._assess_data_quality(dataframe_data),
                'analysis_ready': self._assess_analysis_readiness(dataframe_data)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'pandas_dataframe',
                'source': 'pandas',
                'cognitive_layer': 'data_analysis'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt dataframe data: {str(e)}")
            raise
    
    def adapt_analysis_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt Pandas analysis data to DIX VISION format"""
        try:
            adapted = {
                'data_insight': {
                    'analysis_type': analysis.get('analysis_type', 'unknown'),
                    'analysis_id': analysis.get('analysis_id', 'unknown'),
                    'executed_at': datetime.utcnow().isoformat()
                },
                'insight_metadata': {
                    'input_shape': analysis.get('input_shape', []),
                    'statistics': analysis.get('statistics', {}),
                    'missing_values': analysis.get('missing_values', {}),
                    'data_types': analysis.get('dtypes', {})
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'insight_class': self._classify_analysis(analysis),
                'confidence': self._assess_confidence(analysis),
                'data_integrity': self._assess_data_integrity(analysis),
                'cognitive_value': self._extract_cognitive_value(analysis)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'pandas_analysis',
                'source': 'pandas',
                'cognitive_layer': 'data_insights'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt analysis data: {str(e)}")
            raise
    
    def _classify_dataframe(self, dataframe_data: Dict[str, Any]) -> str:
        """Classify the type of dataframe"""
        shape = dataframe_data.get('shape', [])
        dtypes = dataframe_data.get('dtypes', {})
        
        row_count = shape[0] if len(shape) > 0 else 0
        col_count = shape[1] if len(shape) > 1 else 0
        
        # Check for time series data
        if any('datetime' in str(dtype) for dtype in dtypes.values()):
            return 'time_series_data'
        elif row_count > 100000:
            return 'large_dataset'
        elif col_count > 50:
            return 'wide_dataset'
        elif col_count < 5:
            return 'simple_dataset'
        else:
            return 'standard_dataset'
    
    def _assess_complexity(self, dataframe_data: Dict[str, Any]) -> str:
        """Assess the complexity of the dataframe"""
        shape = dataframe_data.get('shape', [])
        row_count = shape[0] if len(shape) > 0 else 0
        col_count = shape[1] if len(shape) > 1 else 0
        
        if row_count > 100000 or col_count > 100:
            return 'high_complexity'
        elif row_count > 10000 or col_count > 20:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_data_quality(self, dataframe_data: Dict[str, Any]) -> str:
        """Assess the quality of the data"""
        missing_values = dataframe_data.get('missing_values', {})
        dtypes = dataframe_data.get('dtypes', {})
        
        total_missing = sum(missing_values.values())
        total_columns = len(dtypes)
        
        if total_missing == 0:
            return 'complete_data'
        elif total_missing / (total_columns * max(1, dataframe_data.get('row_count', 1))) < 0.05:
            return 'high_quality'
        elif total_missing / (total_columns * max(1, dataframe_data.get('row_count', 1))) < 0.2:
            return 'moderate_quality'
        else:
            return 'low_quality'
    
    def _assess_analysis_readiness(self, dataframe_data: Dict[str, Any]) -> str:
        """Assess if data is ready for analysis"""
        dtypes = dataframe_data.get('dtypes', {})
        
        # Check for object types which might need preprocessing
        has_object = any('object' in str(dtype) for dtype in dtypes.values())
        has_missing = any(missing > 0 for missing in dataframe_data.get('missing_values', {}).values())
        
        if not has_object and not has_missing:
            return 'analysis_ready'
        elif has_object:
            return 'requires_preprocessing'
        elif has_missing:
            return 'missing_data_handling'
        else:
            return 'unknown_status'
    
    def _classify_analysis(self, analysis: Dict[str, Any]) -> str:
        """Classify the type of analysis"""
        analysis_type = analysis.get('analysis_type', '').lower()
        
        if 'statistics' in analysis_type or 'describe' in analysis_type:
            return 'statistical_analysis'
        elif 'group' in analysis_type or 'aggregate' in analysis_type:
            return 'grouping_analysis'
        elif 'merge' in analysis_type or 'join' in analysis_type:
            return 'integration_analysis'
        elif 'missing' in analysis_type:
            return 'quality_analysis'
        else:
            return 'general_analysis'
    
    def _assess_confidence(self, analysis: Dict[str, Any]) -> str:
        """Assess the confidence level of the analysis"""
        input_shape = analysis.get('input_shape', [])
        row_count = input_shape[0] if len(input_shape) > 0 else 0
        
        if row_count > 1000:
            return 'high_confidence'
        elif row_count > 100:
            return 'moderate_confidence'
        else:
            return 'low_confidence'
    
    def _assess_data_integrity(self, analysis: Dict[str, Any]) -> str:
        """Assess data integrity of the analysis"""
        missing_values = analysis.get('missing_values', {})
        total_missing = sum(missing_values.values())
        
        if total_missing == 0:
            return 'integrity_verified'
        elif total_missing < 10:
            return 'minor_issues'
        else:
            return 'integrity_concerns'
    
    def _extract_cognitive_value(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive value from the analysis"""
        analysis_type = analysis.get('analysis_type', '')
        statistics = analysis.get('statistics', {})
        
        return {
            'analytical_depth': 'comprehensive' if statistics else 'basic',
            'actionability': 'high' if statistics else 'low',
            'strategic_value': 'analyzed'
        }
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Pandas data"""
        if isinstance(data, dict):
            if 'shape' in data or 'columns' in data:
                return self.adapt_dataframe_data(data)
            elif 'analysis_type' in data or 'statistics' in data:
                return self.adapt_analysis_data(data)
        
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Pandas data"""
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        if target_format == DataFormat.JSON:
            return self._reverse_json_pandas_data(data)
        
        return data
    
    def _reverse_json_pandas_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Pandas data adaptation"""
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
    adapter = PandasDomainAdapter()
    
    sample_dataframe = {
        'dataframe_id': 'df_12345',
        'shape': [1000, 10],
        'columns': ['col1', 'col2', 'col3'],
        'dtypes': {'col1': 'float64', 'col2': 'int64', 'col3': 'object'},
        'memory_usage': 80000,
        'missing_values': {'col1': 5, 'col2': 0, 'col3': 10}
    }
    
    adapted_dataframe = adapter.adapt_dataframe_data(sample_dataframe)
    print("Adapted dataframe:", adapted_dataframe)
    
    print("Pandas Domain Adapter initialized successfully")
