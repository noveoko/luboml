from bs4 import BeautifulSoup as bs
from collections import defaultdict
from glob import glob
from pathlib import Path
import pickle

def extract_metryki_wolyn_events(path_to_html):
    print(f'Processing {path_to_html}')
    event_dicts = defaultdict(list)
    
    try:
        with open(path_to_html, 'rb') as raw_page:

            rows = raw_page.readlines()
            clean_page = ''
            for row in rows:
                try:
                    clean_page += row.decode('utf-8')
                except UnicodeDecodeError as ue:
                    continue
            soup = bs(clean_page, 'html.parser')
            
            headings = [a.text for a in soup.find_all("h2")]
            tables = soup.find_all("table")
            raw_tables = dict(zip(headings, tables))
            
            for event_type, table in raw_tables.items():
                row_headings = [a.text for a in table.find_all("th")]
                
                for row in table.find_all('tr'):
                    event_dict = dict(zip(row_headings, [a.text for a in row.find_all('td')]))
                    
                    if event_dict:
                        event_dicts[event_type].append(event_dict)
            
        print(f"Success! File {path_to_html} parsed successfully")
        print(f"Total records: {sum(len(records) for records in event_dicts.values())}")
        return event_dicts
    
    except UnicodeDecodeError as ee:
        print(f"Error parsing file {path_to_html}: {ee}")

def extract_all_data_across_directory(path_to_dir):
    try:
        event_dicts = defaultdict(list)
        html_files = glob(f"{path_to_dir}/*.html", recursive=True)
    
        for file in html_files:
            pth = Path(file)
            if not pth.exists():
                raise FileExistsError('Path is not valid: {file}')
            event_dict = extract_metryki_wolyn_events(pth)
        
            if event_dict:
                for key, value in event_dict.items():
                    event_dicts[key].extend(value)
    
        return event_dicts
    except Exception as ee:
        raise ValueError("Nothing was processed!", ee)

all_records = extract_all_data_across_directory(Path(r"..\data"))
with open('records.pickle', 'wb') as f:
    pickle.dump(all_records, f)
