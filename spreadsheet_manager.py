import pandas as pd
import os
from session_manager import session_manager

class SpreadsheetManager:
    @staticmethod
    def update_cell(session_id, row_idx, column, value):
        """Update a single cell in the session dataframe"""
        session = session_manager.get_session(session_id)
        if not session:
            return False, "Session not found"
        
        try:
            df = session['dataframe']
            
            # Type conversion based on existing column type
            # This is a basic implementation; more robust conversion may be needed
            col_type = df[column].dtype
            
            try:
                if pd.api.types.is_numeric_dtype(col_type):
                    if value == '' or value is None:
                        new_value = pd.NA
                    else:
                        new_value = float(value) if '.' in str(value) else int(value)
                else:
                    new_value = value
            except (ValueError, TypeError):
                # Fallback to string if conversion fails
                new_value = value

            df.at[row_idx, column] = new_value
            
            # Update session
            session_manager.update_session(session_id, 'dataframe', df)
            
            # Clear cache for this session
            session['cache'] = {}
            
            return True, "Cell updated successfully"
            
        except Exception as e:
            return False, str(e)

    @staticmethod
    def save_to_file(session_id):
        """Persist the current session dataframe back to the original file on disk"""
        session = session_manager.get_session(session_id)
        if not session:
            return False, "Session not found"

        try:
            df = session['dataframe']
            filepath = session['filepath']
            ext = os.path.splitext(filepath)[1].lower()

            if ext == '.csv':
                df.to_csv(filepath, index=False)
            elif ext in ('.xlsx', '.xls'):
                df.to_excel(filepath, index=False, engine='openpyxl')
            else:
                return False, f"Unsupported file format: {ext}"

            return True, "File saved successfully"

        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_spreadsheet_data(session_id):
        """Get all data for spreadsheet view with row indices"""
        session = session_manager.get_session(session_id)
        if not session:
            return None
        
        df = session['dataframe'].copy()
        
        # Add index as a column for the frontend to use as row IDs
        df_reset = df.reset_index()
        
        # Convert to records handling NaN
        records = df_reset.to_dict('records')
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
        
        return {
            'columns': list(df.columns),
            'data': records
        }

spreadsheet_manager = SpreadsheetManager()
