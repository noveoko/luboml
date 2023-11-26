import pandas as pd
import difflib

# Function for calculating string similarity
def string_similarity(str1, str2):
    # Convert inputs to strings if they are not, handling NaN values
    str1 = str(str1) if pd.notna(str1) else ""
    str2 = str(str2) if pd.notna(str2) else ""
    return difflib.SequenceMatcher(None, str1, str2).ratio()

# Read the CSV files into dataframes
file_paths = [
    "/mnt/data/grodno_birth_father_antoni.csv",
    "/mnt/data/grodno_birth_mother_stefania.csv",
    "/mnt/data/people_born_1927_mother_halina.csv"
]
df_list = [pd.read_csv(file_path) for file_path in file_paths]

# Consolidate the dataframes into a single dataframe
df = pd.concat(df_list).drop_duplicates().reset_index(drop=True)

# Extracting and converting birth year from 'Data urodzenia' column
df['Rok urodzenia'] = pd.to_datetime(df['Data urodzenia'], errors='coerce').dt.year

# Define the target individual
target_individual = {
    'Imię': "<name>",
    'Nazwisko': "<surname>",
    'birth_year': <birth_year>,
    'Miejsce urodzenia': <birth_place>,
    'Imię matki': <mothers_name>,
    'Imię ojca': <fathers_name>
}

# Function to calculate the overall similarity score
def calculate_similarity(row, target):
    score = 0
    # Weight factors for different attributes
    weights = {'name': 1, 'surname': 1, 'birth_year': 0.5, 'birthplace': 1, 'mother': 1, 'father': 1}
    
    # Calculate similarity for each attribute
    score += string_similarity(row['Imię'], target['Imię']) * weights['name']
    score += string_similarity(row['Nazwisko'], target['Nazwisko']) * weights['surname']
    birth_year = row['Rok urodzenia'] if not pd.isna(row['Rok urodzenia']) else target['birth_year']
    score += max(0, 1 - abs(birth_year - target['birth_year']) / 100) * weights['birth_year']
    score += string_similarity(row['Miejsce urodzenia'], target['Miejsce urodzenia']) * weights['birthplace']
    score += string_similarity(row['Imię matki'], target['Imię matki']) * weights['mother']
    score += string_similarity(row['Imię ojca'], target['Imię ojca']) * weights['father']

    return score

# Apply the similarity function to each row in the dataframe
df['similarity_score'] = df.apply(lambda row: calculate_similarity(row, target_individual), axis=1)

# Sort the dataframe based on similarity score
sorted_individuals = df.sort_values(by='similarity_score', ascending=False).drop('similarity_score', axis=1)

# Display the top individuals based on similarity score
print(sorted_individuals.head())
