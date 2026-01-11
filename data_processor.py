import pandas as pd
import numpy as np
from scipy import stats
from config import Config

class DataAnalyzer:
    """Core data analysis and insights generation"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.load_file()
        
    def load_file(self):
        """Load CSV or Excel file"""
        try:
            if self.filepath.endswith('.csv'):
                self.df = pd.read_csv(self.filepath)
            elif self.filepath.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.filepath)
            else:
                raise ValueError("Unsupported file format")
            
            # Auto-detect and convert date columns
            self._detect_dates()
            
            return True
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _detect_dates(self):
        """Automatically detect and parse date columns"""
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    # Try to parse as datetime
                    parsed = pd.to_datetime(self.df[col], errors='coerce')
                    # If more than 50% successfully parsed, convert
                    if parsed.notna().sum() / len(self.df) > 0.5:
                        self.df[col] = parsed
                except:
                    pass
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy/pandas types to JSON-serializable Python types"""
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def get_basic_info(self):
        """Get basic dataset information"""
        info = {
            'rows': int(len(self.df)),
            'columns': int(len(self.df.columns)),
            'memory_usage_mb': float(self.df.memory_usage(deep=True).sum() / (1024 * 1024)),
            'column_types': {str(k): int(v) for k, v in self.df.dtypes.value_counts().to_dict().items()},
            'column_list': list(self.df.columns),
            'duplicates': int(self.df.duplicated().sum()),
            'total_missing': int(self.df.isnull().sum().sum())
        }
        
        return info
    
    def get_statistical_summary(self):
        """Get comprehensive statistical summary"""
        summary = {}
        
        # Numerical columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            desc = self.df[numeric_cols].describe().to_dict()
            # Convert all numpy types to Python types
            summary['numerical'] = self._convert_to_json_serializable(desc)
        
        # Categorical columns
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols:
                value_counts_dict = {k: int(v) for k, v in self.df[col].value_counts().head(5).to_dict().items()}
                cat_summary[col] = {
                    'unique_values': int(self.df[col].nunique()),
                    'most_common': value_counts_dict,
                    'missing': int(self.df[col].isnull().sum())
                }
            summary['categorical'] = cat_summary
        
        # Datetime columns
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            dt_summary = {}
            for col in datetime_cols:
                non_null = self.df[col].dropna()
                if len(non_null) > 0:
                    dt_summary[col] = {
                        'min': non_null.min().isoformat(),
                        'max': non_null.max().isoformat(),
                        'range_days': int((non_null.max() - non_null.min()).days)
                    }
            summary['datetime'] = dt_summary
        
        return summary
    
    def detect_missing_values(self):
        """Analyze missing values"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        
        missing_data = []
        for col in self.df.columns:
            if missing[col] > 0:
                missing_data.append({
                    'column': col,
                    'count': int(missing[col]),
                    'percentage': round(float(missing_pct[col]), 2)
                })
        
        # Sort by count descending
        missing_data.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_missing': int(missing.sum()),
            'columns_with_missing': len(missing_data),
            'details': missing_data
        }
    
    def detect_outliers(self, method='iqr'):
        """Detect outliers using IQR or Z-score method"""
        outliers = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            
            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(col_data))
                outlier_count = (z_scores > 3).sum()
            
            if outlier_count > 0:
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': round(float(outlier_count / len(self.df) * 100), 2)
                }
        
        return outliers
    
    def get_correlations(self):
        """Calculate correlation matrix for numerical columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # Find high correlations (excluding diagonal)
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    high_corr.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': round(float(corr_value), 3)
                    })
        
        # Convert correlation matrix to JSON-serializable format
        matrix_dict = self._convert_to_json_serializable(corr_matrix.to_dict())
        
        return {
            'matrix': matrix_dict,
            'high_correlations': high_corr
        }
    
    def get_value_distributions(self):
        """Analyze value distributions"""
        distributions = {}
        
        # Numerical distributions
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            distributions[col] = {
                'type': 'numerical',
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'std': float(col_data.std()),
                'skewness': float(col_data.skew()),
                'kurtosis': float(col_data.kurtosis())
            }
        
        # Categorical distributions
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            if unique_count <= Config.MAX_CATEGORICAL_UNIQUE:
                value_counts_dict = {k: int(v) for k, v in self.df[col].value_counts().head(10).to_dict().items()}
                distributions[col] = {
                    'type': 'categorical',
                    'unique_count': int(unique_count),
                    'top_values': value_counts_dict
                }
        
        return distributions
    
    def get_column_info(self):
        """Get detailed information about each column"""
        column_info = []
        
        for col in self.df.columns:
            col_data = self.df[col]
            
            info = {
                'name': col,
                'dtype': str(col_data.dtype),
                'non_null': int(col_data.count()),
                'null': int(col_data.isnull().sum()),
                'unique': int(col_data.nunique())
            }
            
            # Add type-specific info
            if pd.api.types.is_numeric_dtype(col_data):
                info['min'] = float(col_data.min()) if col_data.notna().any() else None
                info['max'] = float(col_data.max()) if col_data.notna().any() else None
                info['mean'] = float(col_data.mean()) if col_data.notna().any() else None
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                non_null = col_data.dropna()
                if len(non_null) > 0:
                    info['min'] = non_null.min().isoformat()
                    info['max'] = non_null.max().isoformat()
            
            column_info.append(info)
        
        return column_info
    
    def get_data_quality_score(self):
        """Calculate overall data quality score"""
        score = 100
        
        # Penalize for missing values
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        score -= missing_pct * 0.5
        
        # Penalize for duplicates
        duplicate_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        score -= duplicate_pct * 0.3
        
        # Penalize for outliers
        outliers = self.detect_outliers()
        if outliers:
            avg_outlier_pct = np.mean([v['percentage'] for v in outliers.values()])
            score -= avg_outlier_pct * 0.2
        
        return max(0, min(100, round(score, 1)))
