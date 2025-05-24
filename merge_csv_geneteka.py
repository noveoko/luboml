import pandas as pd
import os

def merge_csv_files(input_directory, output_filename="merged_data.csv"):
    """
    Merges all CSV files found in a specified directory into a single CSV file.

    Args:
        input_directory (str): The path to the directory containing the CSV files.
        output_filename (str): The name of the output merged CSV file.
                                Defaults to "merged_data.csv".
    """
    all_files = []
    merged_data = pd.DataFrame()
    output_path = os.path.join(input_directory, output_filename)

    print(f"Searching for CSV files in: {input_directory}")

    # Collect all CSV file paths
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                all_files.append(file_path)

    if not all_files:
        print(f"No CSV files found in the directory: {input_directory}")
        return

    print(f"Found {len(all_files)} CSV files to merge.")

    # Read and concatenate each CSV file
    for i, file_path in enumerate(all_files):
        try:
            # Read the CSV file. Assuming the first row is the header.
            # If your CSVs don't have headers or have different delimiters,
            # you might need to adjust pd.read_csv parameters (e.g., header=None, sep=';').
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"Successfully read: {os.path.basename(file_path)}")

            if merged_data.empty:
                # If it's the first file, use its content as the base
                merged_data = df
            else:
                # For subsequent files, concatenate them.
                # 'ignore_index=True' resets the index for the new combined DataFrame.
                # 'sort=False' prevents sorting columns alphabetically, preserving original order.
                merged_data = pd.concat([merged_data, df], ignore_index=True, sort=False)

        except pd.errors.EmptyDataError:
            print(f"Warning: CSV file is empty and was skipped: {os.path.basename(file_path)}")
        except FileNotFoundError:
            print(f"Error: File not found: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error processing file {os.path.basename(file_path)}: {e}")

    if not merged_data.empty:
        # Save the merged DataFrame to a new CSV file
        # 'index=False' prevents pandas from writing the DataFrame index as a column.
        merged_data.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nSuccessfully merged {len(all_files)} CSV files into: {output_path}")
        print(f"Total rows in merged file: {len(merged_data)}")
    else:
        print("No data was merged. Check your input CSV files.")

if __name__ == "__main__":
    # --- Configuration ---
    # IMPORTANT: Replace 'path/to/your/csvs' with the actual directory
    # where your downloaded CSV files are located.
    # Example: input_dir = "C:/Users/YourUser/Downloads/metrycal_data"
    # Example: input_dir = "/Users/YourUser/Documents/geneteka_csvs"
    input_dir = "./your_csv_files_directory" # <--- CHANGE THIS PATH

    # You can change the output filename if you wish
    output_file = "all_metrycal_data_merged.csv"
    # --- End Configuration ---

    # Create the directory if it doesn't exist (for testing purposes, or if you plan to place CSVs there)
    if not os.path.exists(input_dir):
        print(f"The specified input directory '{input_dir}' does not exist.")
        print("Please create this directory and place your CSV files inside it, or update the 'input_dir' variable.")
        # Optionally, you can create it for the user if they confirm
        # os.makedirs(input_dir)
        # print(f"Created directory: {input_dir}")
        # print("Please place your CSV files into this directory and run the script again.")
    else:
        merge_csv_files(input_dir, output_file)

