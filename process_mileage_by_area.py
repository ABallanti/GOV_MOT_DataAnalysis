import pandas as pd
import datetime
import numpy as np
import time
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

# Initialize variables
chunk_size = 10_000
max_chunks = None  # For testing, set to None for full processing

# Dictionary to store statistics by area and vehicle type
area_mileage_stats = {}

print("\nProcessing 2023 data...")
start_time = time.time()
total_rows = 0
vehicles_processed = set()

# Plotting the name of the columns of the csv file before processing
print(pd.read_csv('INPUT/test_result_2023.csv', sep='|', nrows=0).columns)

try:
    # First try with utf-8 encoding
    csv_reader = pd.read_csv('INPUT/test_result_2023.csv', 
                            sep='|',
                            usecols=['vehicle_id', 'postcode_area', 'test_mileage', 'first_use_date', 'test_date', 'test_class_id','fuel_type'],
                            chunksize=chunk_size,
                            encoding='utf-8',
                            on_bad_lines='skip')
except UnicodeDecodeError:
    print("UTF-8 encoding failed, trying with latin-1...")
    csv_reader = pd.read_csv('INPUT/test_result_2023.csv', 
                            sep='|',
                            usecols=['vehicle_id', 'postcode_area', 'test_mileage', 'first_use_date', 'test_date', 'test_class_id','fuel_type'],
                            chunksize=chunk_size,
                            encoding='latin-1',
                            on_bad_lines='skip')

# Process data in chunks
chunks_processed = 0
for chunk in csv_reader:
    chunks_processed += 1
    chunk_start_time = time.time()
    
    if max_chunks is not None:
        if chunks_processed > max_chunks:
            print(f"\nReached maximum chunk limit ({max_chunks}). Stopping processing.")
            break
    
    # Convert dates to datetime with error handling
    chunk['first_use_date'] = pd.to_datetime(chunk['first_use_date'], errors='coerce')
    chunk['test_date'] = pd.to_datetime(chunk['test_date'], errors='coerce')
    
    # Filter out rows with invalid dates
    chunk = chunk.dropna(subset=['first_use_date', 'test_date'])
    
    # Filter out rows where test_date is before first_use_date
    chunk = chunk[chunk['test_date'] >= chunk['first_use_date']]
    
    # Calculate vehicle age in years based on test date
    chunk['vehicle_age'] = (chunk['test_date'] - chunk['first_use_date']).dt.days / 365.25
    
    # Filter out rows with invalid age (negative or too old)
    chunk = chunk[(chunk['vehicle_age'] > 0) & (chunk['vehicle_age'] < 100)]  # Assuming no vehicle is older than 100 years
    
    # Calculate yearly mileage
    chunk['yearly_mileage'] = chunk['test_mileage'] / chunk['vehicle_age']
    
    # Update counters
    total_rows += len(chunk)
    vehicles_processed.update(chunk['vehicle_id'].unique())
    
    # Process each row
    for _, row in chunk.iterrows():
        postcode = row['postcode_area']
        vehicle_type = row['test_class_id']
        fuel_type = row['fuel_type']
        yearly_mileage = row['yearly_mileage']
        
        # Skip invalid values
        if not np.isfinite(yearly_mileage) or yearly_mileage < 0 or yearly_mileage > 100000:
            continue
        
        # Initialize postcode area if not exists
        if postcode not in area_mileage_stats:
            area_mileage_stats[postcode] = {
                'vehicle_types': {},
                'total_vehicles': 0,
                'total_mileage': 0,
                'fuel_types': {}
            }
        
        # Initialize vehicle type if not exists
        if vehicle_type not in area_mileage_stats[postcode]['vehicle_types']:
            area_mileage_stats[postcode]['vehicle_types'][vehicle_type] = {
                'yearly_mileages': [],
                'vehicle_count': 0,
                'total_mileage': 0,
            }
        
        # Initialize fuel type if not exists
        if fuel_type not in area_mileage_stats[postcode]['fuel_types']:
            area_mileage_stats[postcode]['fuel_types'][fuel_type] = {
                'yearly_mileages': [],
                'vehicle_count': 0,
                'total_mileage': 0,
            }
        
        # Add to statistics
        area_mileage_stats[postcode]['vehicle_types'][vehicle_type]['yearly_mileages'].append(yearly_mileage)
        area_mileage_stats[postcode]['vehicle_types'][vehicle_type]['vehicle_count'] += 1
        area_mileage_stats[postcode]['vehicle_types'][vehicle_type]['total_mileage'] += yearly_mileage
        
        area_mileage_stats[postcode]['fuel_types'][fuel_type]['vehicle_count'] += 1
        area_mileage_stats[postcode]['fuel_types'][fuel_type]['total_mileage'] += yearly_mileage

        area_mileage_stats[postcode]['total_vehicles'] += 1
        area_mileage_stats[postcode]['total_mileage'] += yearly_mileage
    
    # Calculate progress and timing
    elapsed_time = time.time() - start_time
    rows_per_second = total_rows / elapsed_time if elapsed_time > 0 else 0
    
    # Print progress
    print(f"\rProcessing: {total_rows:,} rows, {len(vehicles_processed):,} vehicles, "
          f"{rows_per_second:.0f} rows/sec, {get_memory_usage():.1f}MB memory", end='')

print(f"\n\nProcessed data: {total_rows:,} rows, {len(vehicles_processed):,} vehicles in {format_time(time.time() - start_time)}")

# Calculate final statistics
print("\nCalculating final statistics...")
start_time = time.time()
results_data = []
vehicle_type_results = []
fuel_type_results = []

# Calculate overall area statistics
for area, data in area_mileage_stats.items():
    if data['total_vehicles'] == 0:
        continue
    
    # Calculate average yearly mileage for the area
    avg_mileage = data['total_mileage'] / data['total_vehicles']
    
    # Collect all yearly mileages for the area
    all_mileages = []
    for type_data in data['vehicle_types'].values():
        all_mileages.extend(type_data['yearly_mileages'])
    
    all_mileages = np.array(all_mileages)
    
    results_data.append({
        'postcode_area': area,
        'average_yearly_mileage': avg_mileage,
        'min_yearly_mileage': np.min(all_mileages),
        'max_yearly_mileage': np.max(all_mileages),
        'percentile_5': np.percentile(all_mileages, 5),
        'percentile_95': np.percentile(all_mileages, 95),
        'vehicle_count': data['total_vehicles']
    })
    
    # Calculate vehicle type statistics
    for vehicle_type, type_data in data['vehicle_types'].items():
        if type_data['vehicle_count'] == 0:
            continue
            
        type_mileages = np.array(type_data['yearly_mileages'])
        avg_type_mileage = type_data['total_mileage'] / type_data['vehicle_count']
        
        vehicle_type_results.append({
            'postcode_area': area,
            'vehicle_type': vehicle_type,
            'average_yearly_mileage': avg_type_mileage,
            'min_yearly_mileage': np.min(type_mileages),
            'max_yearly_mileage': np.max(type_mileages),
            'percentile_5': np.percentile(type_mileages, 5),
            'percentile_95': np.percentile(type_mileages, 95),
            'vehicle_count': type_data['vehicle_count']
        })

    # Calculate fuel type statistics
    for fuel_type, fuel_data in data['fuel_types'].items():
        if fuel_data['vehicle_count'] == 0:
            continue
    
        fuel_mileages = np.array(fuel_data['total_mileage'])
        avg_fuel_mileage = fuel_mileages.sum()/fuel_data['vehicle_count']
                
        fuel_type_results.append({
            'postcode_area': area,
            'fuel_type': fuel_type,
            'average_yearly_mileage': avg_fuel_mileage,
            'min_yearly_mileage': np.min(fuel_mileages),
            'max_yearly_mileage': np.max(fuel_mileages),
            'vehicle_count': fuel_data['vehicle_count'],
            'total_mileage': fuel_data['total_mileage'],
            'percentile_5': np.percentile(fuel_mileages, 5),
            'percentile_95': np.percentile(fuel_mileages, 95)
        })

# Create DataFrames and save results
if results_data:
    results_df = pd.DataFrame(results_data)
    vehicle_type_df = pd.DataFrame(vehicle_type_results)
    fuel_type_df = pd.DataFrame(fuel_type_results)
    # Sort results
    results_df = results_df.sort_values('average_yearly_mileage', ascending=False)
    vehicle_type_df = vehicle_type_df.sort_values(['postcode_area', 'average_yearly_mileage'], ascending=[True, False])
    
    # Save results
    output_file = 'OUTPUT/yearly_mileage_2023.csv'
    vehicle_type_output_file = 'OUTPUT/yearly_mileage_by_vehicle_type_2023.csv'
    fuel_type_output_file = 'OUTPUT/yearly_mileage_by_fuel_type_2023.csv'
    
    results_df.to_csv(output_file, index=False)
    vehicle_type_df.to_csv(vehicle_type_output_file, index=False)
    fuel_type_df.to_csv(fuel_type_output_file, index=False)

    print(f"\nResults saved to {output_file}")
    print(f"Vehicle type statistics saved to {vehicle_type_output_file}")
    print(f"Fuel type statistics saved to {fuel_type_output_file}")
    
    # Print summary statistics
    print("\nProcessing complete!")
    print(f"\nNumber of postcode areas processed: {len(results_df)}")
    print(f"\nSample of statistics for top 5 areas by average yearly mileage:")
    pd.set_option('display.float_format', lambda x: '{:,.0f}'.format(x) if abs(x) >= 1000 else '{:,.2f}'.format(x))
    print(results_df.head().to_string())
    
    # Print vehicle type statistics sample
    print(f"\nSample of vehicle type statistics for first 5 postcode areas:")
    print(vehicle_type_df.head(10).to_string())
    
    # Print fuel type statistics sample
    print(f"\nSample of fuel type statistics for first 5 postcode areas:")
    print(fuel_type_df.head(10).to_string())
    
    # Print overall statistics
    print(f"\nOverall Statistics (2023):")
    print(f"Average yearly mileage across all areas: {results_df['average_yearly_mileage'].mean():,.0f}")
    
    if not results_df['average_yearly_mileage'].empty and not results_df['average_yearly_mileage'].isna().all():
        max_mileage = results_df['average_yearly_mileage'].max()
        min_mileage = results_df['average_yearly_mileage'].min()
        
        if not pd.isna(max_mileage):
            max_area = results_df.loc[results_df['average_yearly_mileage'].idxmax(), 'postcode_area']
            print(f"Highest average yearly mileage: {max_mileage:,.0f} (Area: {max_area})")
        
        if not pd.isna(min_mileage):
            min_area = results_df.loc[results_df['average_yearly_mileage'].idxmin(), 'postcode_area']
            print(f"Lowest average yearly mileage: {min_mileage:,.0f} (Area: {min_area})")
    
    print(f"\nTotal vehicles processed: {results_df['vehicle_count'].sum():,}")
    print(f"Final memory usage: {get_memory_usage():.1f}MB")
    print(f"Total processing time: {format_time(time.time() - start_time)}")
else:
    print("\nNo valid data found") 