import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class PredictionEngine:
    """Machine learning predictions and forecasting"""
    
    def __init__(self, dataframe):
        self.df = dataframe
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
    def auto_detect_problem_type(self, target_column):
        """Determine if it's regression, classification, or time series"""
        if target_column not in self.df.columns:
            return None
        
        col_data = self.df[target_column]
        
        # Check if target is numeric
        if pd.api.types.is_numeric_dtype(col_data):
            unique_count = col_data.nunique()
            # If few unique values, likely classification
            if unique_count < 10:
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'
    
    def time_series_forecast(self, date_column, value_column, periods=30):
        """Forecast future values for time series data"""
        if date_column not in self.datetime_cols or value_column not in self.numeric_cols:
            return None
        
        try:
            # Prepare data
            df_ts = self.df[[date_column, value_column]].dropna()
            df_ts = df_ts.sort_values(date_column)
            df_ts = df_ts.set_index(date_column)
            
            # Simple linear trend forecast
            X = np.arange(len(df_ts)).reshape(-1, 1)
            y = df_ts[value_column].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Forecast
            future_X = np.arange(len(df_ts), len(df_ts) + periods).reshape(-1, 1)
            forecast = model.predict(future_X)
            
            # Generate future dates
            last_date = df_ts.index[-1]
            freq = pd.infer_freq(df_ts.index)
            if freq is None:
                freq = 'D'  # Default to daily
            
            future_dates = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
            
            # Calculate trend
            trend = "increasing" if model.coef_[0] > 0 else "decreasing"
            trend_strength = abs(model.coef_[0])
            
            return {
                'forecast': [
                    {'date': date.isoformat(), 'value': float(val)}
                    for date, val in zip(future_dates, forecast)
                ],
                'historical': [
                    {'date': date.isoformat(), 'value': float(val)}
                    for date, val in zip(df_ts.index, y)
                ],
                'trend': trend,
                'trend_strength': float(trend_strength),
                'r2_score': float(r2_score(y, model.predict(X)))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def regression_analysis(self, target_column, feature_columns=None):
        """Perform regression analysis"""
        if target_column not in self.numeric_cols:
            return None
        
        try:
            # Auto-select features if not provided
            if feature_columns is None:
                feature_columns = [col for col in self.numeric_cols if col != target_column]
            
            if len(feature_columns) == 0:
                return {'error': 'No suitable feature columns found'}
            
            # Prepare data
            df_clean = self.df[feature_columns + [target_column]].dropna()
            
            if len(df_clean) < 10:
                return {'error': 'Insufficient data for regression'}
            
            X = df_clean[feature_columns].values
            y = df_clean[target_column].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train models
            lr_model = LinearRegression()
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            
            lr_model.fit(X_train, y_train)
            rf_model.fit(X_train, y_train)
            
            # Predictions
            lr_pred = lr_model.predict(X_test)
            rf_pred = rf_model.predict(X_test)
            
            # Metrics
            lr_r2 = r2_score(y_test, lr_pred)
            lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
            
            rf_r2 = r2_score(y_test, rf_pred)
            rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
            
            # Feature importance (Random Forest)
            feature_importance = [
                {'feature': feat, 'importance': float(imp)}
                for feat, imp in zip(feature_columns, rf_model.feature_importances_)
            ]
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            return {
                'target': target_column,
                'features': feature_columns,
                'linear_regression': {
                    'r2_score': float(lr_r2),
                    'rmse': float(lr_rmse),
                    'coefficients': [float(c) for c in lr_model.coef_]
                },
                'random_forest': {
                    'r2_score': float(rf_r2),
                    'rmse': float(rf_rmse),
                    'feature_importance': feature_importance
                },
                'best_model': 'Random Forest' if rf_r2 > lr_r2 else 'Linear Regression',
                'sample_predictions': [
                    {
                        'actual': float(y_test[i]),
                        'predicted': float(rf_pred[i]) if rf_r2 > lr_r2 else float(lr_pred[i])
                    }
                    for i in range(min(10, len(y_test)))
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def classification_analysis(self, target_column, feature_columns=None):
        """Perform classification analysis"""
        try:
            # Auto-select numerical features if not provided
            if feature_columns is None:
                feature_columns = [col for col in self.numeric_cols if col != target_column]
            
            if len(feature_columns) == 0:
                return {'error': 'No suitable feature columns found'}
            
            # Prepare data
            df_clean = self.df[feature_columns + [target_column]].dropna()
            
            if len(df_clean) < 10:
                return {'error': 'Insufficient data for classification'}
            
            # Encode target if necessary
            le = LabelEncoder()
            y = le.fit_transform(df_clean[target_column])
            X = df_clean[feature_columns].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train models
            lr_model = LogisticRegression(max_iter=1000, random_state=42)
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            
            lr_model.fit(X_train_scaled, y_train)
            rf_model.fit(X_train, y_train)
            
            # Predictions
            lr_pred = lr_model.predict(X_test_scaled)
            rf_pred = rf_model.predict(X_test)
            
            # Metrics
            lr_acc = accuracy_score(y_test, lr_pred)
            rf_acc = accuracy_score(y_test, rf_pred)
            
            # Feature importance (Random Forest)
            feature_importance = [
                {'feature': feat, 'importance': float(imp)}
                for feat, imp in zip(feature_columns, rf_model.feature_importances_)
            ]
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            return {
                'target': target_column,
                'features': feature_columns,
                'classes': le.classes_.tolist(),
                'logistic_regression': {
                    'accuracy': float(lr_acc)
                },
                'random_forest': {
                    'accuracy': float(rf_acc),
                    'feature_importance': feature_importance
                },
                'best_model': 'Random Forest' if rf_acc > lr_acc else 'Logistic Regression'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def trend_analysis(self, column):
        """Analyze trends in a numerical column"""
        if column not in self.numeric_cols:
            return None
        
        try:
            col_data = self.df[column].dropna()
            
            # Calculate moving averages
            if len(col_data) >= 7:
                ma_7 = col_data.rolling(window=7).mean()
            else:
                ma_7 = None
            
            # Detect trend direction
            X = np.arange(len(col_data)).reshape(-1, 1)
            y = col_data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            trend_direction = "upward" if model.coef_[0] > 0 else "downward"
            trend_slope = float(model.coef_[0])
            
            # Volatility
            volatility = float(col_data.std())
            
            return {
                'column': column,
                'trend_direction': trend_direction,
                'trend_slope': trend_slope,
                'volatility': volatility,
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'current_value': float(col_data.iloc[-1]),
                'change_from_mean': float(col_data.iloc[-1] - col_data.mean())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_prediction_recommendations(self):
        """Suggest what predictions can be made with this dataset"""
        recommendations = []
        
        # Check for time series potential
        if len(self.datetime_cols) > 0 and len(self.numeric_cols) > 0:
            for dt_col in self.datetime_cols:
                for num_col in self.numeric_cols:
                    recommendations.append({
                        'type': 'time_series_forecast',
                        'description': f'Forecast {num_col} over time',
                        'date_column': dt_col,
                        'value_column': num_col
                    })
        
        # Check for regression potential
        if len(self.numeric_cols) >= 2:
            for target in self.numeric_cols:
                features = [col for col in self.numeric_cols if col != target]
                if len(features) > 0:
                    recommendations.append({
                        'type': 'regression',
                        'description': f'Predict {target} using {len(features)} features',
                        'target': target,
                        'features': features[:5]  # Top 5 features
                    })
        
        return recommendations[:5]  # Return top 5 recommendations
