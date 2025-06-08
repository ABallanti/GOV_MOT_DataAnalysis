# This script creates an interactive map of the number of vehicles by fuel type in the UK
# It uses the postcode areas shapefile and the vehicle count data
# The map is saved as an HTML file

import geopandas as gpd
import folium
from folium import GeoJson
import branca.colormap as cm
import json
import pandas as pd
import numpy as np

# Fuel type options:
# CNG (CN) - Compressed Natural Gas
# Diesel (DI)
# Electric Diesel (ED)
# Electric (EL)
# Fuel Cells (FC)
# Gas (GA)
# Gas Bi-Fuel (GB)
# Gas Diesel (GD)
# Hybrid Electric (HY)
# LNG (LN) - Liquefied Natural Gas
# LPG (LP) - Liquefied Petroleum Gas
# Other (OT)
# Petrol (PE)
# Steam (ST)

# Configuration - Change this value to show different fuel types
FUEL_TYPE = 'EL'  # Options: 'CN', 'DI', 'ED', 'EL', 'FC', 'GA', 'GB', 'GD', 'HY', 'LN', 'LP', 'OT', 'PE', 'ST'

# Dictionary of fuel types and their descriptions
FUEL_TYPES = {
    'CN': 'Compressed Natural Gas',
    'DI': 'Diesel',
    'ED': 'Electric Diesel',
    'EL': 'Electric',
    'FC': 'Fuel Cells',
    'GA': 'Gas',
    'GB': 'Gas Bi-Fuel',
    'GD': 'Gas Diesel',
    'HY': 'Hybrid Electric',
    'LN': 'Liquefied Natural Gas',
    'LP': 'Liquefied Petroleum Gas',
    'OT': 'Other',
    'PE': 'Petrol',
    'ST': 'Steam'
}

# Read the fuel type data
print(f"Reading vehicle count data for {FUEL_TYPES[FUEL_TYPE]} ({FUEL_TYPE})...")
fuel_type_data = pd.read_csv('OUTPUT/yearly_mileage_by_fuel_type_2023.csv')

# Filter data for selected fuel type
type_data = fuel_type_data[fuel_type_data['fuel_type'] == FUEL_TYPE]

# Clean the data - remove any NaN or infinite values
type_data = type_data.replace([np.inf, -np.inf], np.nan)
type_data = type_data.dropna(subset=['vehicle_count'])

# Read the Areas shapefile
print("Reading postcode areas from shapefile...")
postcode_areas = gpd.read_file('INPUT/distribution/Areas.shp')

# Convert to WGS84 (latitude/longitude) - required for Folium
postcode_areas = postcode_areas.to_crs(epsg=4326)

# Merge with geographical data
type_postcode_areas = postcode_areas.merge(
    type_data,
    left_on='name',
    right_on='postcode_area',
    how='left'
)

# Create color map
min_count = float(type_data['vehicle_count'].min())
max_count = float(type_data['vehicle_count'].max())

print(f"Creating color map with range: {min_count:,.0f} to {max_count:,.0f}")

colormap = cm.LinearColormap(
    colors=['green', 'yellow', 'red'],
    vmin=min_count,
    vmax=max_count,
    caption=f'Number of Vehicles - {FUEL_TYPES[FUEL_TYPE]} ({FUEL_TYPE})'
)

# Create a base map centered on UK
center_lat = postcode_areas.geometry.centroid.y.mean()
center_lon = postcode_areas.geometry.centroid.x.mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles='CartoDB positron'
)

# Style function
def style_function(feature):
    count = feature['properties'].get('vehicle_count', None)
    return {
        'fillColor': colormap(count) if count is not None else '#gray',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    }

# Highlight function
def highlight_function(feature):
    return {
        'weight': 3,
        'fillOpacity': 0.9
    }

# Add the GeoJson data to the map
GeoJson(
    json.loads(type_postcode_areas.to_json()),
    name=f'{FUEL_TYPES[FUEL_TYPE]} ({FUEL_TYPE})',
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['name', 'vehicle_count'],
        aliases=['Area:', 'Number of Vehicles:'],
        localize=True,
        sticky=True,
        formatter="""
            function(props) {
                return '<div>' +
                    '<b>Area:</b> ' + props.name + '<br>' +
                    '<b>Number of Vehicles:</b> ' + Number(props.vehicle_count).toLocaleString() +
                '</div>';
            }
        """
    )
).add_to(m)

# Add the colormap to the map
colormap.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
output_file = f'OUTPUT/uk_postcode_fuel_count_{FUEL_TYPE}.html'
print(f"\nSaving interactive map to {output_file}")
m.save(output_file)
print("Done! Open the HTML file in a web browser to view the interactive map.")