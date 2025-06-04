# EV Map - Vehicle Mileage Analysis Project

## Project Overview
This project analyzes vehicle mileage data to calculate yearly mileage differences across different postcode areas. We use postcode areas that are in two-three characters (e.g., M) as these are the data available in the MOT database. It processes large datasets using chunked processing as the input files are very large (4GB each). It provides detailed statistics about vehicle usage patterns.

## Purpose
The main purpose of this project is to:
- Calculate yearly mileage differences for vehicles between consecutive years
- Group and analyze mileage data by postcode areas
- Generate statistical insights about vehicle usage patterns
- Identify areas with highest and lowest average yearly mileage
- Monitor processing performance and resource usage

## Project Structure
```
EV_Map/
├── INPUT/
│   ├── test_result_2022.csv  # Input data file for 2022
│   └── test_result_2023.csv  # Input data file for 2023
├── OUTPUT/
│   ├── vehicle_mileages_*.json  # Raw vehicle mileage data
│   └── yearly_mileage_difference_*.csv  # Generated output files
├── process_mileage_by_area.py  # Main processing script
└── architecture.md          # This documentation file
```

## Data Structure

### Input Data
The input files contain the following columns:
- `vehicle_id`: Unique identifier for each vehicle
- `postcode_area`: Geographic area code of where the MOT test has been carried out
- `test_mileage`: Vehicle mileage at test time
- `test_date`: Date of the test
- `test_class_id`: Vehicle test class identifier

### Output Data
1. JSON file containing raw vehicle mileage data
2. CSV file with the following statistics for each postcode area:
   - `postcode_area`: Geographic area code
   - `average_yearly_mileage`: Mean yearly mileage difference
   - `min_yearly_mileage`: Minimum yearly mileage difference
   - `max_yearly_mileage`: Maximum yearly mileage difference
   - `percentile_5`: 5th percentile of yearly mileage differences
   - `percentile_95`: 95th percentile of yearly mileage differences
   - `vehicle_count`: Number of vehicles in the area

## Key Components

### Configuration Variables
- `chunk_size`: Number of rows to process at once (default: 10,000)
- `max_chunks`: Maximum number of chunks to process (None for full processing)
- `TARGET_YEAR`: Year to analyze (default: 2023)
- `PREVIOUS_YEAR`: Year before target year (default: 2022)

### Data Structures
1. `vehicle_mileages`: Dictionary storing mileage data for each vehicle
   ```python
   {
       'vehicle_id': {
           'current_year': {'mileage': value, 'postcode': value, 'test_class_id': value},
           'previous_year': {'mileage': value, 'postcode': value, 'test_class_id': value}
       }
   }
   ```

2. `area_mileage_differences`: Dictionary storing statistics for each postcode area
   ```python
   {
       'postcode_area': {
           'differences': [list of mileage differences],
           'vehicle_count': count,
           'total_difference': sum of differences
       }
   }
   ```

## Processing Flow
1. **Initial Setup**
   - Configure target years and processing parameters
   - Initialize data structures and monitoring tools

2. **Data Loading and Processing**
   - Process 2022 data first:
     - Read input CSV file in chunks
     - Track progress and memory usage
     - Store previous year data
   - Process 2023 data:
     - Read input CSV file in chunks
     - Track progress and memory usage
     - Store current year data
   - Handle different file encodings (UTF-8, Latin-1)
   - Extract relevant columns

3. **Data Processing**
   - Calculate yearly mileage differences
   - Group data by postcode areas
   - Apply filters for valid mileage differences
   - Track vehicles with data in both years

4. **Statistics Generation**
   - Calculate various statistics for each area
   - Generate summary statistics
   - Create output files (JSON and CSV)

## Performance Monitoring
The script includes comprehensive performance tracking:
- Real-time progress display:
  - Number of rows processed
  - Number of unique vehicles found
  - Processing speed (rows per second)
  - Current memory usage
- Timing information for each major step
- Memory usage monitoring
- Processing speed metrics

## Output and Reporting
The script generates:
1. A JSON file with raw vehicle mileage data
2. A detailed CSV file with area-wise statistics
3. Console output with:
   - Processing progress and speed
   - Memory usage statistics
   - Summary statistics
   - Top 5 areas by average yearly mileage
   - Overall statistics including min/max/average values
   - Processing time for each step

## Error Handling
- Handles different file encodings
- Skips bad lines in input data
- Validates mileage differences
- Provides informative error messages
- Monitors and reports memory usage

## Usage
1. Place input data files in the INPUT directory:
   - test_result_2022.csv
   - test_result_2023.csv
2. Run the script:
   ```bash
   python process_mileage_by_area.py
   ```
3. Check the OUTPUT directory for results:
   - vehicle_mileages_*.json
   - yearly_mileage_difference_*.csv

## Dependencies
- pandas: Data manipulation and analysis
- numpy: Numerical computations
- datetime: Date handling
- psutil: System and process utilities
- time: Time tracking

## Future Improvements
Potential areas for enhancement:
- Add command-line arguments for configuration
- Implement parallel processing for faster execution
- Add data visualization capabilities
- Include more statistical measures
- Add data validation and cleaning steps
- Implement checkpointing for long-running processes
- Add progress bar visualization
- Implement memory optimization strategies 