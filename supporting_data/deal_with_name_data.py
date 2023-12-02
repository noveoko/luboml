import pandas as pd

# Assuming df is your DataFrame

# Feature for common surnames
df['Same Surname'] = df.duplicated('Surname', keep=False).astype(int)

# Feature for common father's name
df['Same Father Name'] = df.duplicated("Father's name", keep=False).astype(int)

# Feature for common mother's name
df['Same Mother Name'] = df.duplicated("Mother's name", keep=False).astype(int)

# Frequency of surnames in the dataset
surname_counts = df['Surname'].value_counts().to_dict()
df['Surname Frequency'] = df['Surname'].map(surname_counts)

# One-hot encoding for 'Parish' and 'Place'
df = pd.get_dummies(df, columns=['Parish', 'Place'])

# Process 'Remarks' column (if it contains structured information like dates)
# For example, extract year from 'Remarks' if it contains dates

# Drop original name columns if they are no longer needed after feature engineering
# df.drop(['Name', 'Surname', "Father's name", "Mother's name", "Mother's surname", 'Remarks'], axis=1, inplace=True)

# Your DataFrame is now ready for use in a regression tree model
