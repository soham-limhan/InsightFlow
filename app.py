from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pandas as pd
from config import Config
from session_manager import session_manager
from data_processor import DataAnalyzer
from visualizer import ChartGenerator
from predictor import PredictionEngine
from data_cleaner import DataCleaner
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize folders
Config.init_app()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page with file upload"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV and Excel files are allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Load and create session
        try:
            analyzer = DataAnalyzer(filepath)
            session_id = session_manager.create_session(filename, filepath, analyzer.df)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'filename': filename,
                'redirect': url_for('dashboard', session_id=session_id)
            })
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Failed to process file: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Display analysis dashboard"""
    session = session_manager.get_session(session_id)
    if not session:
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', 
                         session_id=session_id, 
                         filename=session['filename'])

@app.route('/api/insights/<session_id>')
def get_insights(session_id):
    """Get statistical insights"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check cache
        cached = session_manager.get_cached_result(session_id, 'insights')
        if cached:
            return jsonify(cached)
        
        # Analyze data
        analyzer = DataAnalyzer(session['filepath'])
        
        insights = {
            'basic_info': analyzer.get_basic_info(),
            'statistical_summary': analyzer.get_statistical_summary(),
            'missing_values': analyzer.detect_missing_values(),
            'outliers': analyzer.detect_outliers(),
            'correlations': analyzer.get_correlations(),
            'distributions': analyzer.get_value_distributions(),
            'column_info': analyzer.get_column_info(),
            'data_quality_score': analyzer.get_data_quality_score()
        }
        
        # Cache results
        session_manager.cache_result(session_id, 'insights', insights)
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/<session_id>')
def get_visualizations(session_id):
    """Get visualization data"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check cache
        cached = session_manager.get_cached_result(session_id, 'visualizations')
        if cached:
            return jsonify(cached)
        
        # Generate visualizations
        viz_gen = ChartGenerator(session['dataframe'])
        
        visualizations = {
            'distribution_plots': viz_gen.create_distribution_plots(),
            'correlation_heatmap': viz_gen.create_correlation_heatmap(),
            'categorical_charts': viz_gen.create_categorical_charts(),
            'time_series_plots': viz_gen.create_time_series_plots(),
            'scatter_matrix': viz_gen.create_scatter_matrix(),
            'missing_data_viz': viz_gen.create_missing_data_viz(),
            'summary_statistics_chart': viz_gen.create_summary_statistics_chart()
        }
        
        # Cache results
        session_manager.cache_result(session_id, 'visualizations', visualizations)
        
        return jsonify(visualizations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/<session_id>')
def get_predictions(session_id):
    """Get prediction recommendations and results"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        predictor = PredictionEngine(session['dataframe'])
        
        recommendations = predictor.get_prediction_recommendations()
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def run_prediction():
    """Run a specific prediction"""
    try:
        data = request.json
        session_id = data.get('session_id')
        pred_type = data.get('type')
        
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        predictor = PredictionEngine(session['dataframe'])
        
        if pred_type == 'time_series_forecast':
            result = predictor.time_series_forecast(
                data.get('date_column'),
                data.get('value_column'),
                data.get('periods', 30)
            )
        elif pred_type == 'regression':
            result = predictor.regression_analysis(
                data.get('target'),
                data.get('features')
            )
        elif pred_type == 'classification':
            result = predictor.classification_analysis(
                data.get('target'),
                data.get('features')
            )
        elif pred_type == 'trend':
            result = predictor.trend_analysis(data.get('column'))
        else:
            return jsonify({'error': 'Invalid prediction type'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<session_id>')
def get_data(session_id):
    """Get paginated, filtered, and sorted data"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        df = session['dataframe'].copy()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        search = request.args.get('search', '')
        
        # Search across all columns
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
        
        # Sort
        if sort_by and sort_by in df.columns:
            ascending = sort_order == 'asc'
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Pagination
        total_rows = len(df)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        df_page = df.iloc[start_idx:end_idx]
        
        # Convert to records, handling datetime
        records = df_page.to_dict('records')
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
        
        return jsonify({
            'data': records,
            'total_rows': total_rows,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_rows + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleaning/suggestions/<session_id>')
def get_cleaning_suggestions(session_id):
    """Get data cleaning suggestions"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        cleaner = DataCleaner(session['dataframe'])
        suggestions = cleaner.suggest_cleaning_steps()
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleaning/apply', methods=['POST'])
def apply_cleaning():
    """Apply a cleaning action"""
    try:
        data = request.json
        session_id = data.get('session_id')
        action_type = data.get('type')
        
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        cleaner = DataCleaner(session['dataframe'])
        
        if action_type == 'fill_missing':
            success, message = cleaner.handle_missing_values(
                data.get('column'),
                data.get('method', 'mean')
            )
        elif action_type == 'handle_outliers':
            success, message = cleaner.remove_outliers(
                data.get('column'),
                data.get('method', 'iqr')
            )
        elif action_type == 'remove_duplicates':
            success, message = cleaner.remove_duplicates()
        elif action_type == 'drop_column':
            success, message = cleaner.drop_column(data.get('column'))
        else:
            return jsonify({'error': 'Invalid action type'}), 400
        
        if success:
            # Update session with cleaned data
            session_manager.update_session(session_id, 'dataframe', cleaner.get_cleaned_dataframe())
            # Clear cache since data changed
            session['cache'] = {}
            
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/<session_id>')
def export_data(session_id):
    """Export cleaned data to CSV"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Create temporary export file
        export_filename = f"cleaned_{session['filename']}"
        export_path = os.path.join(Config.UPLOAD_FOLDER, export_filename)
        
        # Save to CSV
        session['dataframe'].to_csv(export_path, index=False)
        
        return send_file(export_path, as_attachment=True, download_name=export_filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """Delete session and cleanup files"""
    try:
        session_manager.delete_session(session_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
