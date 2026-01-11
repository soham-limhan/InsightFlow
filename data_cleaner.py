import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

class DataCleaner:
    """Data cleaning and transformation utilities"""
    
    def __init__(self, dataframe):
        self.df = dataframe.copy()
        self.original_df = dataframe.copy()
        self.cleaning_history = []
        
    def suggest_cleaning_steps(self):
        """Analyze data and suggest cleaning steps"""
        suggestions = []
        
        # Check for missing values
        missing = self.df.isnull().sum()
        cols_with_missing = missing[missing > 0]
        
        if len(cols_with_missing) > 0:
            for col in cols_with_missing.index:
                missing_pct = (cols_with_missing[col] / len(self.df)) * 100
                
                if missing_pct > 50:
                    suggestions.append({
                        'type': 'drop_column',
                        'column': col,
                        'reason': f'{missing_pct:.1f}% missing values',
                        'severity': 'high'
                    })
                elif pd.api.types.is_numeric_dtype(self.df[col]):
                    suggestions.append({
                        'type': 'fill_missing',
                        'column': col,
                        'method': 'mean',
                        'reason': f'{missing_pct:.1f}% missing values',
                        'severity': 'medium'
                    })
                else:
                    suggestions.append({
                        'type': 'fill_missing',
                        'column': col,
                        'method': 'mode',
                        'reason': f'{missing_pct:.1f}% missing values',
                        'severity': 'medium'
                    })
        
        # Check for duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            suggestions.append({
                'type': 'remove_duplicates',
                'count': int(duplicates),
                'reason': f'{duplicates} duplicate rows found',
                'severity': 'high'
            })
        
        # Check for outliers
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR))).sum()
            
            if outliers > 0:
                outlier_pct = (outliers / len(self.df)) * 100
                if outlier_pct > 1:
                    suggestions.append({
                        'type': 'handle_outliers',
                        'column': col,
                        'count': int(outliers),
                        'reason': f'{outlier_pct:.1f}% outliers detected',
                        'severity': 'low'
                    })
        
        # Check for constant columns
        for col in self.df.columns:
            if self.df[col].nunique() == 1:
                suggestions.append({
                    'type': 'drop_column',
                    'column': col,
                    'reason': 'Column has only one unique value',
                    'severity': 'medium'
                })
        
        return suggestions
    
    def handle_missing_values(self, column, method='mean'):
        """Fill missing values using specified method"""
        try:
            if method == 'drop':
                self.df = self.df.dropna(subset=[column])
                action = f"Dropped rows with missing {column}"
                
            elif method == 'mean' and pd.api.types.is_numeric_dtype(self.df[column]):
                fill_value = self.df[column].mean()
                self.df[column].fillna(fill_value, inplace=True)
                action = f"Filled {column} missing values with mean ({fill_value:.2f})"
                
            elif method == 'median' and pd.api.types.is_numeric_dtype(self.df[column]):
                fill_value = self.df[column].median()
                self.df[column].fillna(fill_value, inplace=True)
                action = f"Filled {column} missing values with median ({fill_value:.2f})"
                
            elif method == 'mode':
                fill_value = self.df[column].mode()[0]
                self.df[column].fillna(fill_value, inplace=True)
                action = f"Filled {column} missing values with mode ({fill_value})"
                
            elif method == 'forward_fill':
                self.df[column].fillna(method='ffill', inplace=True)
                action = f"Forward filled {column} missing values"
                
            elif method == 'backward_fill':
                self.df[column].fillna(method='bfill', inplace=True)
                action = f"Backward filled {column} missing values"
                
            else:
                return False, "Invalid method"
            
            self.cleaning_history.append(action)
            return True, action
            
        except Exception as e:
            return False, str(e)
    
    def remove_outliers(self, column, method='iqr'):
        """Remove outliers from numerical column"""
        try:
            if not pd.api.types.is_numeric_dtype(self.df[column]):
                return False, "Column must be numerical"
            
            original_len = len(self.df)
            
            if method == 'iqr':
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                self.df = self.df[(self.df[column] >= lower_bound) & (self.df[column] <= upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
                self.df = self.df[z_scores < 3]
            
            removed = original_len - len(self.df)
            action = f"Removed {removed} outliers from {column} using {method.upper()} method"
            self.cleaning_history.append(action)
            
            return True, action
            
        except Exception as e:
            return False, str(e)
    
    def normalize_data(self, columns, method='minmax'):
        """Normalize numerical columns"""
        try:
            if method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'standard':
                scaler = StandardScaler()
            else:
                return False, "Invalid normalization method"
            
            self.df[columns] = scaler.fit_transform(self.df[columns])
            
            action = f"Normalized columns {columns} using {method} scaling"
            self.cleaning_history.append(action)
            
            return True, action
            
        except Exception as e:
            return False, str(e)
    
    def encode_categorical(self, column, method='onehot'):
        """Encode categorical variables"""
        try:
            if method == 'onehot':
                dummies = pd.get_dummies(self.df[column], prefix=column)
                self.df = pd.concat([self.df, dummies], axis=1)
                self.df.drop(column, axis=1, inplace=True)
                action = f"One-hot encoded {column}"
                
            elif method == 'label':
                le = LabelEncoder()
                self.df[column] = le.fit_transform(self.df[column].astype(str))
                action = f"Label encoded {column}"
            else:
                return False, "Invalid encoding method"
            
            self.cleaning_history.append(action)
            return True, action
            
        except Exception as e:
            return False, str(e)
    
    def detect_duplicates(self):
        """Find duplicate rows"""
        duplicates = self.df[self.df.duplicated(keep=False)]
        return {
            'count': int(self.df.duplicated().sum()),
            'percentage': round(float(self.df.duplicated().sum() / len(self.df) * 100), 2),
            'duplicate_rows': duplicates.head(20).to_dict('records') if len(duplicates) > 0 else []
        }
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        original_len = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = original_len - len(self.df)
        
        action = f"Removed {removed} duplicate rows"
        self.cleaning_history.append(action)
        
        return True, action
    
    def drop_column(self, column):
        """Drop a column"""
        try:
            self.df.drop(column, axis=1, inplace=True)
            action = f"Dropped column {column}"
            self.cleaning_history.append(action)
            return True, action
        except Exception as e:
            return False, str(e)
    
    def get_cleaned_dataframe(self):
        """Return the cleaned dataframe"""
        return self.df
    
    def get_cleaning_history(self):
        """Return list of all cleaning actions performed"""
        return self.cleaning_history
    
    def reset(self):
        """Reset to original dataframe"""
        self.df = self.original_df.copy()
        self.cleaning_history = []
        return True, "Data reset to original state"
