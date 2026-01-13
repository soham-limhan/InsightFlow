import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd
import numpy as np
from config import Config

class ChartGenerator:
    """Generate interactive visualizations using Plotly"""
    
    def __init__(self, dataframe):
        self.df = dataframe
        
    def create_distribution_plots(self):
        """Create distribution plots for numerical columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        charts = []
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            
            # Histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=col_data.tolist(),  # Convert to plain list
                name=col,
                nbinsx=30,
                marker=dict(
                    color='rgba(99, 102, 241, 0.7)',
                    line=dict(color='rgba(99, 102, 241, 1)', width=1)
                )
            ))
            
            fig.update_layout(
                title=f'Distribution of {col}',
                xaxis_title=col,
                yaxis_title='Frequency',
                template='plotly_dark',
                height=Config.DEFAULT_CHART_HEIGHT,
                showlegend=False
            )
            
            charts.append({
                'column': col,
                'type': 'histogram',
                'data': pio.to_json(fig, validate=False, remove_uids=False, engine='json')
            })
            
            # Box plot
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=col_data.tolist(),  # Convert to plain list
                name=col,
                marker=dict(color='rgba(139, 92, 246, 0.7)'),
                boxmean='sd'
            ))
            
            fig_box.update_layout(
                title=f'Box Plot of {col}',
                yaxis_title=col,
                template='plotly_dark',
                height=Config.DEFAULT_CHART_HEIGHT,
                showlegend=False
            )
            
            charts.append({
                'column': col,
                'type': 'boxplot',
                'data': pio.to_json(fig_box, validate=False, remove_uids=False, engine='json')
            })
        
        return charts
    
    def create_correlation_heatmap(self):
        """Create correlation heatmap"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # Convert to plain lists for JSON serialization
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values.tolist(),  # Convert to plain list
            x=corr_matrix.columns.tolist(),  # Convert to plain list
            y=corr_matrix.columns.tolist(),  # Convert to plain list
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.tolist(),  # Convert to plain list
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Correlation Heatmap',
            template='plotly_dark',
            height=max(Config.DEFAULT_CHART_HEIGHT, len(numeric_cols) * 30),
            width=max(Config.DEFAULT_CHART_WIDTH, len(numeric_cols) * 30)
        )
        
        return pio.to_json(fig, validate=False, remove_uids=False, engine='json')
    
    def create_categorical_charts(self):
        """Create bar/pie charts for categorical columns"""
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        charts = []
        
        for col in categorical_cols:
            unique_count = self.df[col].nunique()
            
            if unique_count <= Config.MAX_CATEGORICAL_UNIQUE:
                value_counts = self.df[col].value_counts().head(10)
                
                # Bar chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=value_counts.index.tolist(),  # Convert to plain list
                    y=value_counts.values.tolist(),  # Convert to plain list
                    marker=dict(
                        color=value_counts.values.tolist(),  # Convert to plain list
                        colorscale='Viridis',
                        showscale=True
                    ),
                    text=value_counts.values.tolist(),  # Convert to plain list
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title=f'Distribution of {col} (Top 10)',
                    xaxis_title=col,
                    yaxis_title='Count',
                    template='plotly_dark',
                    height=Config.DEFAULT_CHART_HEIGHT
                )
                
                charts.append({
                    'column': col,
                    'type': 'bar',
                    'data': pio.to_json(fig, validate=False, remove_uids=False, engine='json')
                })
                
                # Pie chart (only if unique count <= 10)
                if unique_count <= 10:
                    fig_pie = go.Figure()
                    fig_pie.add_trace(go.Pie(
                        labels=value_counts.index.tolist(),  # Convert to plain list
                        values=value_counts.values.tolist(),  # Convert to plain list
                        hole=0.3,
                        marker=dict(colors=px.colors.qualitative.Set3)
                    ))
                    
                    fig_pie.update_layout(
                        title=f'Proportion of {col}',
                        template='plotly_dark',
                        height=Config.DEFAULT_CHART_HEIGHT
                    )
                    
                    charts.append({
                        'column': col,
                        'type': 'pie',
                        'data': pio.to_json(fig_pie, validate=False, remove_uids=False, engine='json')
                    })
        
        return charts
    
    def create_time_series_plots(self):
        """Create time series plots if datetime columns exist"""
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        charts = []
        
        for dt_col in datetime_cols:
            # Sort by datetime
            df_sorted = self.df.sort_values(dt_col)
            
            for num_col in numeric_cols:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sorted[dt_col].tolist(),  # Convert to plain list
                    y=df_sorted[num_col].tolist(),  # Convert to plain list
                    mode='lines+markers',
                    name=num_col,
                    line=dict(color='rgba(59, 130, 246, 0.8)', width=2),
                    marker=dict(size=4)
                ))
                
                fig.update_layout(
                    title=f'{num_col} over {dt_col}',
                    xaxis_title=dt_col,
                    yaxis_title=num_col,
                    template='plotly_dark',
                    height=Config.DEFAULT_CHART_HEIGHT,
                    hovermode='x unified'
                )
                
                charts.append({
                    'datetime_column': dt_col,
                    'value_column': num_col,
                    'type': 'timeseries',
                    'data': pio.to_json(fig, validate=False, remove_uids=False, engine='json')
                })
        
        return charts
    
    def create_scatter_matrix(self):
        """Create pairwise scatter plot matrix"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        # Limit to first 5 numeric columns for performance
        cols_to_plot = numeric_cols[:5]
        
        fig = px.scatter_matrix(
            self.df[cols_to_plot].dropna(),
            dimensions=cols_to_plot,
            color_discrete_sequence=['rgba(99, 102, 241, 0.6)'],
            template='plotly_dark',
            height=800,
            title='Scatter Plot Matrix'
        )
        
        fig.update_traces(diagonal_visible=False, showupperhalf=False)
        
        return pio.to_json(fig, validate=False, remove_uids=False, engine='json')
    
    def create_missing_data_viz(self):
        """Visualize missing data patterns"""
        # Create a binary matrix: 1 for missing, 0 for present
        missing_matrix = self.df.isnull().astype(int)
        
        if missing_matrix.sum().sum() == 0:
            return None
        
        # Only show columns with missing values
        cols_with_missing = missing_matrix.columns[missing_matrix.sum() > 0]
        
        if len(cols_with_missing) == 0:
            return None
        
        # Sample rows if too many
        if len(self.df) > 1000:
            sample_indices = np.random.choice(len(self.df), 1000, replace=False)
            missing_matrix = missing_matrix.iloc[sample_indices]
        
        fig = go.Figure(data=go.Heatmap(
            z=missing_matrix[cols_with_missing].T.values,
            y=cols_with_missing,
            x=list(range(len(missing_matrix))),
            colorscale=[[0, 'rgba(34, 197, 94, 0.3)'], [1, 'rgba(239, 68, 68, 0.8)']],
            showscale=False,
            hovertemplate='Column: %{y}<br>Row: %{x}<br>Missing: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Missing Data Pattern',
            xaxis_title='Rows (sample)',
            yaxis_title='Columns',
            template='plotly_dark',
            height=max(300, len(cols_with_missing) * 30)
        )
        
        return pio.to_json(fig, validate=False, remove_uids=False, engine='json')
    
    def create_summary_statistics_chart(self):
        """Create visual summary of key statistics"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return None
        
        stats_data = []
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            stats_data.append({
                'Column': col,
                'Mean': col_data.mean(),
                'Median': col_data.median(),
                'Std Dev': col_data.std(),
                'Min': col_data.min(),
                'Max': col_data.max()
            })
        
        stats_df = pd.DataFrame(stats_data)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        metrics = ['Mean', 'Median', 'Std Dev']
        colors = ['rgba(59, 130, 246, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(236, 72, 153, 0.7)']
        
        for metric, color in zip(metrics, colors):
            fig.add_trace(go.Bar(
                name=metric,
                x=stats_df['Column'],
                y=stats_df[metric],
                marker=dict(color=color)
            ))
        
        fig.update_layout(
            title='Statistical Summary Comparison',
            xaxis_title='Columns',
            yaxis_title='Value',
            template='plotly_dark',
            barmode='group',
            height=Config.DEFAULT_CHART_HEIGHT
        )
        
        return pio.to_json(fig, validate=False, remove_uids=False, engine='json')
