# InsightFlow

A comprehensive web-based data analysis application that transforms CSV/Excel files into actionable insights with AI-powered analysis, interactive visualizations, and predictive analytics.

![Data Quality Score](https://img.shields.io/badge/Data%20Quality-96.9%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)

## Features

### 📊 Statistical Analysis
- Comprehensive descriptive statistics
- Missing value detection and analysis
- Outlier detection (IQR & Z-score methods)
- Correlation analysis with automatic detection
- Data quality scoring (0-100%)

### 📈 Interactive Visualizations
- Distribution plots (histograms, box plots)
- Correlation heatmaps
- Categorical charts (bar, pie)
- Time series plots
- Scatter matrices
- Powered by Plotly for full interactivity

### 🔮 Predictive Analytics
- Time series forecasting
- Regression analysis (Linear & Random Forest)
- Classification models
- Trend analysis & detection
- Feature importance ranking

### 🧹 Data Cleaning
- Automated cleaning suggestions
- Missing value handling (multiple strategies)
- Outlier removal
- Duplicate detection and removal
- Data normalization & encoding
- Cleaning history tracking

### 💎 Modern UI/UX
- Dark mode with glassmorphism effects
- Responsive design
- Drag-and-drop file upload
- Interactive data explorer
- Real-time updates

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or navigate to the project directory:
```powershell
cd "c:\ProjectDevEnv\Data Cleaner"
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Run the application:
```powershell
python app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

1. **Upload Data**: Drag and drop your CSV or Excel file onto the landing page
2. **Explore Overview**: View dataset statistics and data quality metrics
3. **Analyze Insights**: Review numerical, categorical, and correlation insights
4. **Visualize Data**: Explore interactive charts and graphs
5. **Run Predictions**: Execute forecasting and trend analysis
6. **Explore Data**: Use the interactive table with search, sort, and filter
7. **Clean Data**: Apply automated cleaning suggestions
8. **Export Results**: Download cleaned data

## Project Structure

```
c:\ProjectDevEnv\Data Cleaner\
├── app.py                    # Flask application (main)
├── config.py                 # Configuration settings
├── session_manager.py        # Session lifecycle management
├── data_processor.py         # Core analysis engine
├── visualizer.py             # Chart generation (Plotly)
├── predictor.py              # ML predictions
├── data_cleaner.py           # Data transformation utilities
├── requirements.txt          # Python dependencies
├── sample_data.csv           # Sample dataset for testing
├── templates/
│   ├── index.html            # Landing page
│   └── dashboard.html        # Main dashboard
└── static/
    ├── css/
    │   └── style.css         # Design system
    └── js/
        ├── upload.js         # Upload logic
        └── dashboard.js      # Dashboard interactivity
```

## Technologies

### Backend
- **Flask**: Web framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning
- **Statsmodels**: Statistical models
- **Plotly**: Interactive visualizations

### Frontend
- **HTML5**: Structure
- **Vanilla CSS**: Styling with custom design system
- **JavaScript**: Interactivity
- **Plotly.js**: Chart rendering

## Features in Detail

### Statistical Analysis Engine
The `DataAnalyzer` class provides comprehensive analysis:
- Automatic date detection and parsing
- Type inference for numerical, categorical, and datetime columns
- Statistical summaries with proper type handling
- Correlation matrix generation
- Data quality assessment

### Visualization Generation
The `ChartGenerator` creates interactive Plotly charts:
- Automatic chart type selection based on data
- Color-coded visualizations
- Responsive design
- Export capabilities

### Prediction Engine
The `PredictionEngine` offers multiple ML models:
- Auto problem type detection (regression/classification/time series)
- Model comparison (Linear vs Random Forest)
- Performance metrics (R², RMSE, accuracy)
- Feature importance analysis

### Data Cleaning
The `DataCleaner` provides smart suggestions:
- Context-aware recommendations
- One-click apply functionality
- Reversible operations
- Complete history tracking

## API Endpoints

- `GET /` - Landing page
- `POST /upload` - File upload
- `GET /dashboard/<session_id>` - Dashboard view
- `GET /api/insights/<session_id>` - Statistical insights
- `GET /api/visualizations/<session_id>` - Visualization data
- `GET /api/predictions/<session_id>` - Prediction recommendations
- `POST /api/predict` - Execute predictions
- `GET /api/data/<session_id>` - Paginated data
- `GET /api/cleaning/suggestions/<session_id>` - Cleaning suggestions
- `POST /api/cleaning/apply` - Apply cleaning operations
- `GET /export/<session_id>` - Export cleaned data

## Configuration

Edit `config.py` to customize:
- Upload file size limits (default: 100MB)
- Allowed file extensions (CSV, XLSX, XLS)
- Session timeout (default: 1 hour)
- Visualization parameters
- Processing constraints

## Sample Data

A sample dataset (`sample_data.csv`) is included with:
- 69 rows of sales data
- Multiple data types (datetime, categorical, numerical)
- Intentional missing values for testing cleaning features

## Testing

Run the application and test with the sample dataset:
```powershell
python app.py
```

Then navigate to http://127.0.0.1:5000 and upload `sample_data.csv`.

Expected results:
- **Rows**: 69
- **Columns**: 7
- **Data Quality**: ~96.9%
- **Missing Values**: 2 cells
- **Visualizations**: Bar charts, pie charts, distributions

## Performance

- **Session Caching**: Results cached to avoid recomputation
- **Pagination**: Large datasets handled with pagination (50 rows/page)
- **Lazy Loading**: Visualizations loaded on-demand
- **Debounced Search**: 500ms delay for search optimization

## Security

- File type validation
- File size limits
- Session isolation
- Secure file handling
- Input sanitization

## Browser Compatibility

Tested and working on:
- Chrome/Edge (Chromium-based)
- Modern browsers with ES6 support

## Limitations

- Maximum file size: 100MB
- Categorical columns: Limited to 50 unique values for visualization
- Time series: Requires regular intervals for forecasting
- Scatter matrix: Limited to first 5 numerical columns

## Future Enhancements

- PDF report generation
- More ML models (XGBoost, Neural Networks)
- Real-time collaboration
- Data source connectors (SQL databases, APIs)
- Advanced time series models (ARIMA, Prophet)

## Troubleshooting

### ModuleNotFoundError
Install missing packages:
```powershell
pip install -r requirements.txt
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### JSON Serialization Errors
The app includes automatic NumPy/Pandas type conversion. If issues persist, ensure you're using the latest version of the code.

## License

This project was created as a demonstration of data analysis capabilities.

## Author

Built with Flask, Pandas, Plotly, and Scikit-learn.

---

**Happy Analyzing! 📊✨**
