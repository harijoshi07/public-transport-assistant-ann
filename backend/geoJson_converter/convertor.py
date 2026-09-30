import pandas as pd
import geojson

# Read CSV file into a DataFrame
input_csv = 'stationinfo.csv'  # Replace with the path to your CSV file
output_geojson = 'output.geojson'  # Replace with the desired output GeoJSON file name

try:
    df = pd.read_csv(input_csv, sep=';')
    print("File read successfully.")
except FileNotFoundError:
    print(f"File '{input_csv}' not found. Please check the file path.")
    exit()

# Remove quotation signs from each column
df = df.applymap(lambda x: x.strip('"'))

# Convert DataFrame to GeoJSON features
features = []
for index, row in df.iterrows():
    station_name = row['station_english_name']
    latitude = float(row['station_latitude'])
    longitude = float(row['station_longitude'])

    feature = geojson.Feature(
        geometry=geojson.Point((longitude, latitude)),
        properties={'name': station_name}
    )

    features.append(feature)

# Create a GeoJSON FeatureCollection
feature_collection = geojson.FeatureCollection(features)

# Serialize the GeoJSON object to a string
geojson_string = geojson.dumps(feature_collection, indent=2)

# Save the GeoJSON to a file
with open(output_geojson, 'w') as f:
    f.write(geojson_string)

print(f"GeoJSON conversion complete. Output saved to '{output_geojson}'.")
