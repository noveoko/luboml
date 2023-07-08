import pickle
from pathlib import Path

records = None

with open(Path(r'records.pickle'), 'rb') as f:
    records = pickle.load(f)
    for name, data in records.items():
        print(name, len(data))

    deaths = records['Zgony']
    births = records['Urodzenia']
    marriages = records['Śluby']
    notes = records['Spisy']
    try:
        marriages.extend(records['¦luby']) #TODO: Fix this at the root (file ingestion)
        print(len(marriages))
    except Exception as ee:
        print("Cannot merge dicts")


    print("Births", births[0])
    print("Marriages", marriages[0])
    print("Deaths", deaths[0])
    print("Notes", notes[0])

