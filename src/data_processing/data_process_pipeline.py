import os
from config import DATA_PATHS
import raw_data_processing
import analysis
import graph

def ensure_directories():
    for path in DATA_PATHS.values():
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"create directory: {directory}")

def run_full_pipeline():
    # Run the full data processing pipeline
    print("=" * 50)
    print("starting data processing pipeline")
    print("=" * 50)

    # Ensure directories exist
    ensure_directories()
    
    try:
        # Step 1: Raw data processing
        print("\nStep 1/3: Process raw data")
        raw_data_processing.main()
        
        # Step 2: Paper classification
        print("\nStep 2/3: Paper classification")
        analysis.main()

        # Step 3: Build co-authorship network
        print("\nStep 3/3: Build co-authorship network")
        graph.main()
        
        print("\n" + "=" * 50)
        print("Data processing pipeline complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error occurred during processing: {e}")
        raise

if __name__ == "__main__":
    run_full_pipeline()