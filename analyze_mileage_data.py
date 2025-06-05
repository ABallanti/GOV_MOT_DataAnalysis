import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for better visualizations
plt.style.use('default')  # Using default style instead of seaborn
sns.set_theme()  # This will set a nice seaborn theme without requiring the style

def plot_vehicle_counts(df):
    """Plot the number of vehicles by vehicle type"""
    print("\nPlotting vehicle counts by vehicle type...")
    
    # Group by vehicle type and sum the counts
    vehicle_counts = df.groupby('vehicle_type')['vehicle_count'].sum().reset_index()
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(vehicle_counts['vehicle_type'], vehicle_counts['vehicle_count'])
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom')
    
    plt.title('Number of Vehicles by Type')
    plt.xlabel('Vehicle Type')
    plt.ylabel('Number of Vehicles')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('OUTPUT/vehicle_counts_by_type.png')
    plt.close()

def plot_mileage_by_area(df):
    """Plot average, max, min mileage by postcode area for each vehicle type"""
    print("\nPlotting mileage statistics by area...")
    
    # Get unique vehicle types
    vehicle_types = df['vehicle_type'].unique()
    
    for v_type in vehicle_types:
        # Filter data for current vehicle type
        type_data = df[df['vehicle_type'] == v_type]
        
        # Sort by average mileage
        type_data = type_data.sort_values('average_yearly_mileage', ascending=False)
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        
        # Plot average mileage with error bars showing min-max and 5-95 percentiles
        plt.errorbar(range(len(type_data)), 
                    type_data['average_yearly_mileage'],
                    yerr=[type_data['average_yearly_mileage'] - type_data['min_yearly_mileage'],
                          type_data['max_yearly_mileage'] - type_data['average_yearly_mileage']],
                    fmt='o',
                    capsize=5,
                    label='Average Mileage (Min-Max)',
                    color='#CCCCCC',  # Light grey color
                    alpha=0.7)
        
        # Add 5th and 95th percentiles as additional error bars
        plt.errorbar(range(len(type_data)), 
                    type_data['average_yearly_mileage'],
                    yerr=[type_data['average_yearly_mileage'] - type_data['percentile_5'],
                          type_data['percentile_95'] - type_data['average_yearly_mileage']],
                    fmt='o',
                    capsize=5,
                    label='Average Mileage (5th-95th Percentile)',
                    color='red',
                    alpha=0.7)
        
        # Customize the plot
        plt.title(f'Mileage Statistics by Postcode Area - Vehicle Type {v_type}')
        plt.xlabel('Postcode Areas')
        plt.ylabel('Yearly Mileage')
        plt.xticks(range(len(type_data)), type_data['postcode_area'], rotation=90)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(f'OUTPUT/mileage_by_area_type_{v_type}.png')
        plt.close()

# Generate a summary report for the entire dataset
def generate_summary_report(df, report_type='vehicle'):
    """Generate a summary report of the data"""
    print("\nGenerating summary report...")
    
    # Calculate total number of vehicles
    total_vehicles = df['vehicle_count'].sum()
    
    # Calculate overall statistics
    if report_type == 'vehicle':
        group_by = 'vehicle_type'
    else:  # fuel type
        group_by = 'fuel_type'
        
    overall_stats = df.groupby(group_by).agg({
        'vehicle_count': 'sum',
        'average_yearly_mileage': ['mean', 'min', 'max'],
        'min_yearly_mileage': 'min',
        'max_yearly_mileage': 'max'
    }).round(2)
    
    # Save the report
    with open(f'OUTPUT/summary_report_{report_type}.txt', 'w') as f:
        f.write(f"Mileage Analysis Summary Report - {report_type.title()}\n")
        f.write("==============================\n\n")
        f.write(f"Total number of vehicles: {total_vehicles:,}\n")
        f.write(f"Statistics by {report_type.title()}:\n")
        f.write(overall_stats.to_string())
    
    print(f"Summary report saved to OUTPUT/summary_report_{report_type}.txt")

def main():
    # Load both datasets
    vehicle_df = pd.read_csv('OUTPUT/yearly_mileage_by_vehicle_type_2023.csv')
    fuel_df = pd.read_csv('OUTPUT/yearly_mileage_by_fuel_type_2023.csv')
    
    # Generate visualizations and reports for vehicle types
    plot_vehicle_counts(vehicle_df)
    plot_mileage_by_area(vehicle_df)
    generate_summary_report(vehicle_df, 'vehicle')
    
    # Generate reports for fuel types
    generate_summary_report(fuel_df, 'fuel')
    
    print("\nAnalysis complete! Check the OUTPUT directory for results.")

if __name__ == "__main__":
    main() 