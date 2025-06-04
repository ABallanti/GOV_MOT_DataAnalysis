import pandas as pd
import sqlite3
import time

def test_csv():
    print("\nTesting CSV approach...")
    start_time = time.time()
    
    # Read CSV in chunks
    min_id = float('inf')
    chunk_size = 100000
    
    try:
        csv_reader = pd.read_csv('INPUT/test_result_2022.csv', 
                                sep='|',
                                usecols=['vehicle_id'],
                                chunksize=chunk_size,
                                encoding='utf-8',
                                on_bad_lines='skip')
    except UnicodeDecodeError:
        csv_reader = pd.read_csv('INPUT/test_result_2022.csv', 
                                sep='|',
                                usecols=['vehicle_id'],
                                chunksize=chunk_size,
                                encoding='latin-1',
                                on_bad_lines='skip')
    
    for chunk in csv_reader:
        chunk_min = chunk['vehicle_id'].min()
        min_id = min(min_id, chunk_min)
    
    end_time = time.time()
    print(f"CSV approach took {end_time - start_time:.2f} seconds")
    print(f"Lowest vehicle_id: {min_id}")
    return end_time - start_time

def test_sqlite():
    print("\nTesting SQLite approach...")
    start_time = time.time()
    
    # Create SQLite database and import data
    conn = sqlite3.connect('test_results.db')
    
    # Create table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            vehicle_id INTEGER
        )
    ''')
    
    # Import data in chunks
    chunk_size = 100000
    try:
        csv_reader = pd.read_csv('INPUT/test_result_2022.csv', 
                                sep='|',
                                usecols=['vehicle_id'],
                                chunksize=chunk_size,
                                encoding='utf-8',
                                on_bad_lines='skip')
    except UnicodeDecodeError:
        csv_reader = pd.read_csv('INPUT/test_result_2022.csv', 
                                sep='|',
                                usecols=['vehicle_id'],
                                chunksize=chunk_size,
                                encoding='latin-1',
                                on_bad_lines='skip')
    
    for chunk in csv_reader:
        chunk.to_sql('test_results', conn, if_exists='append', index=False)
    
    # Create index for faster querying
    conn.execute('CREATE INDEX IF NOT EXISTS idx_vehicle_id ON test_results(vehicle_id)')
    
    # Find minimum vehicle_id
    cursor = conn.execute('SELECT MIN(vehicle_id) FROM test_results')
    min_id = cursor.fetchone()[0]
    
    end_time = time.time()
    print(f"SQLite approach took {end_time - start_time:.2f} seconds")
    print(f"Lowest vehicle_id: {min_id}")
    
    # Clean up
    conn.close()
    return end_time - start_time

if __name__ == "__main__":
    print("Starting performance comparison...")
    
    # Run CSV test
    csv_time = test_csv()
    
    # Run SQLite test
    sqlite_time = test_sqlite()
    
    # Print comparison
    print("\nPerformance Comparison:")
    print(f"CSV approach: {csv_time:.2f} seconds")
    print(f"SQLite approach: {sqlite_time:.2f} seconds")
    print(f"SQLite is {csv_time/sqlite_time:.1f}x faster") 