from visualizer import ChartGenerator
import pandas as pd
import json

# Load sample data
df = pd.read_csv('sample_data.csv')
print("=" * 60)
print("TESTING FIXED VISUALIZATION")
print("=" * 60)

# Create visualization generator
viz = ChartGenerator(df)

# Test distribution plots
print("\n1. Testing Distribution Plots...")
dist_plots = viz.create_distribution_plots()
print(f"   [OK] Generated {len(dist_plots)} distribution plots")

# Check if data is now plain JSON (not binary)
first_hist = [p for p in dist_plots if p['type'] == 'histogram'][0]
data_json = json.loads(first_hist['data'])
trace = data_json['data'][0]
x_data = trace.get('x')

if isinstance(x_data, list):
    print(f"   [SUCCESS] X data is now a plain array with {len(x_data)} values")
    print(f"   [SUCCESS] Sample values: {x_data[:5]}")
elif isinstance(x_data, dict) and 'bdata' in x_data:
    print(f"   [FAILED] Still using binary encoding")
    print(f"   [FAILED] X data: {x_data}")
else:
    print(f"   [UNKNOWN] X data type is {type(x_data)}")

# Test correlation heatmap
print("\n2. Testing Correlation Heatmap...")
corr_heatmap = viz.create_correlation_heatmap()
if corr_heatmap:
    corr_data = json.loads(corr_heatmap)
    if corr_data.get('data'):
        z_data = corr_data['data'][0].get('z')
        if isinstance(z_data, list) and len(z_data) > 0 and isinstance(z_data[0], list):
            print(f"   [SUCCESS] Heatmap data is plain array ({len(z_data)}x{len(z_data[0])})")
        else:
            print(f"   [FAILED] Unexpected heatmap data format")
else:
    print("   [INFO] No heatmap (expected if < 2 numeric columns)")

# Test categorical charts
print("\n3. Testing Categorical Charts...")
cat_charts = viz.create_categorical_charts()
print(f"   [OK] Generated {len(cat_charts)} categorical charts")
if cat_charts:
    first_cat = cat_charts[0]
    cat_data = json.loads(first_cat['data'])
    cat_trace = cat_data['data'][0]
    
    if first_cat['type'] == 'bar':
        x_cat = cat_trace.get('x')
        y_cat = cat_trace.get('y')
        if isinstance(x_cat, list) and isinstance(y_cat, list):
            print(f"   [SUCCESS] Bar chart has plain arrays (x:{len(x_cat)}, y:{len(y_cat)})")
        else:
            print(f"   [FAILED] Bar chart data is not plain arrays")
    elif first_cat['type'] == 'pie':
        labels = cat_trace.get('labels')
        values = cat_trace.get('values')
        if isinstance(labels, list) and isinstance(values, list):
            print(f"   [SUCCESS] Pie chart has plain arrays")
        else:
            print(f"   [FAILED] Pie chart data is not plain arrays")

# Test time series
print("\n4. Testing Time Series Plots...")
ts_plots = viz.create_time_series_plots()
print(f"   [OK] Generated {len(ts_plots)} time series plots")

# Test summary statistics chart
print("\n5. Testing Summary Statistics Chart...")
summary_chart = viz.create_summary_statistics_chart()
if summary_chart:
    summary_data = json.loads(summary_chart)
    print(f"   [OK] Generated summary statistics chart")
else:
    print("   [INFO] No summary chart")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print(f"Distribution plots: {len(dist_plots)}")
print(f"Categorical charts: {len(cat_charts)}")
print(f"Time series plots: {len(ts_plots)}")
print(f"Correlation heatmap: {'Yes' if corr_heatmap else 'No'}")
print(f"Summary chart: {'Yes' if summary_chart else 'No'}")
