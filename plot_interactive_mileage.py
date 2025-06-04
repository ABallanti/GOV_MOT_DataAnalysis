import geopandas as gpd
import folium
from folium import GeoJson
import branca.colormap as cm
import json
import pandas as pd
import numpy as np

# Configuration - Change this value to show different vehicle types
VEHICLE_TYPE = 7 # Options: 1, 2, 3, 4, etc.

# Read the mileage data
print(f"Reading average mileage data for vehicle type {VEHICLE_TYPE}...")
vehicle_type_data = pd.read_csv('OUTPUT/yearly_mileage_by_vehicle_type_2023.csv')

# Filter data for selected vehicle type
type_data = vehicle_type_data[vehicle_type_data['vehicle_type'] == VEHICLE_TYPE]

# Clean the data - remove any NaN or infinite values
type_data = type_data.replace([np.inf, -np.inf], np.nan)
type_data = type_data.dropna(subset=['average_yearly_mileage'])

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
min_mileage = float(type_data['average_yearly_mileage'].min())
max_mileage = float(type_data['average_yearly_mileage'].max())

print(f"Creating color map with range: {min_mileage:,.0f} to {max_mileage:,.0f}")

colormap = cm.LinearColormap(
    colors=['green', 'yellow', 'red'],
    vmin=min_mileage,
    vmax=max_mileage,
    caption=f'Average Yearly Mileage - Vehicle Type {VEHICLE_TYPE}'
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
    mileage = feature['properties'].get('average_yearly_mileage', None)
    return {
        'fillColor': colormap(mileage) if mileage is not None else '#gray',
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

# Popup function
def popup_function(feature):
    props = feature['properties']
    postcode = props['name']
    
    return f"""
        <div style='width: 300px;'>
            <h3 style='margin: 0 0 10px 0;'>{postcode}</h3>
            <div style='margin-bottom: 10px;'>
                <b>Vehicle Type {VEHICLE_TYPE} Statistics:</b><br>
                Average Yearly Mileage: {props.get('average_yearly_mileage', 'No data'):,.0f} miles<br>
                Number of Vehicles: {props.get('vehicle_count', 'No data'):,}<br>
                Min: {props.get('min_yearly_mileage', 'No data'):,.0f} miles<br>
                Max: {props.get('max_yearly_mileage', 'No data'):,.0f} miles<br>
                5th %: {props.get('percentile_5', 'No data'):,.0f} miles<br>
                95th %: {props.get('percentile_95', 'No data'):,.0f} miles
            </div>
        </div>
    """

# Add the GeoJson data to the map
GeoJson(
    json.loads(type_postcode_areas.to_json()),
    name=f'Vehicle Type {VEHICLE_TYPE}',
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['name', 'average_yearly_mileage', 'vehicle_count'],
        aliases=['Area:', 'Avg Yearly Mileage:', 'Vehicles:'],
        localize=True,
        sticky=True,
        formatter="""
            function(props) {
                return '<div>' +
                    '<b>Area:</b> ' + props.name + '<br>' +
                    '<b>Avg Yearly Mileage:</b> ' + Math.round(Number(props.average_yearly_mileage)).toLocaleString() + ' miles<br>' +
                    '<b>Vehicles:</b> ' + Number(props.vehicle_count).toLocaleString() +
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
output_file = f'OUTPUT/uk_postcode_mileage_map_type_{VEHICLE_TYPE}.html'
print(f"\nSaving interactive map to {output_file}")
m.save(output_file)
print("Done! Open the HTML file in a web browser to view the interactive map.") 