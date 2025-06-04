# EV Map - Vehicle Mileage Analysis

This project processes vehicle test data to analyze yearly mileage patterns across different postcode areas and vehicle types.

## Features

- Processes vehicle test data from CSV files
- Calculates yearly mileage statistics by postcode area
- Provides detailed analysis by vehicle type
- Generates comprehensive reports with statistical measures
- Memory-efficient processing using chunked data reading

## Requirements

- Python 3.x
- pandas
- numpy
- psutil

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Place your input data file in the `INPUT` directory as `test_result_2023.csv` with the following columns:
- vehicle_id
- postcode_area
- test_mileage
- first_use_date
- test_date
- test_class_id

Run the script:
```bash
python process_mileage_by_area.py
```

Results will be saved in the `OUTPUT` directory:
- `yearly_mileage_2023.csv`: Overall statistics by postcode area
- `yearly_mileage_by_vehicle_type_2023.csv`: Statistics broken down by vehicle type

## Output Format

The script generates two CSV files:

1. `yearly_mileage_2023.csv`:
   - postcode_area
   - average_yearly_mileage
   - min_yearly_mileage
   - max_yearly_mileage
   - percentile_5
   - percentile_95
   - vehicle_count

2. `yearly_mileage_by_vehicle_type_2023.csv`:
   - postcode_area
   - vehicle_type
   - average_yearly_mileage
   - min_yearly_mileage
   - max_yearly_mileage
   - percentile_5
   - percentile_95
   - vehicle_count 