import os

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Detect Vercel serverless environment
    IS_VERCEL = os.environ.get('VERCEL') == '1'
    
    # Upload settings — use /tmp on Vercel (read-only filesystem)
    if IS_VERCEL:
        UPLOAD_FOLDER = '/tmp/uploads'
        CACHE_FOLDER = '/tmp/cache'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
        CACHE_FOLDER = os.path.join(BASE_DIR, 'cache')
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Visualization settings
    MAX_PLOT_POINTS = 10000  # Maximum points to plot for performance
    DEFAULT_CHART_HEIGHT = 400
    DEFAULT_CHART_WIDTH = 600
    
    # Prediction settings
    MIN_ROWS_FOR_PREDICTION = 10
    FORECAST_PERIODS = 30  # Default forecast periods
    
    # Data processing settings
    CHUNK_SIZE = 10000  # For processing large files in chunks
    MAX_CATEGORICAL_UNIQUE = 50  # Max unique values to treat as categorical
    
    @staticmethod
    def init_app():
        """Initialize application folders"""
        try:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            os.makedirs(Config.CACHE_FOLDER, exist_ok=True)
        except OSError:
            pass  # Silently skip on read-only filesystems

