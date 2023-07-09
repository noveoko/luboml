from pydantic import BaseModel
from typing import Optional

births_0 =  {'Dzień': '13', 'Miesiąc': '6', 'Rok': '1741', 'Parafia': 'Szumsk', 'Imiona': 'Antoni', 'Nazwisko': 'Błaszczuk', 'Miejscowość': 'Załuże', 'Imię Ojca': 'Jakub', 'Imię Matki': 'Regina', 'Nazwisko rodowe matki': '', 'Chrzestni i uwagi': 'Tomasz Rarzebiński, Jadwiga Franczycha', 'Sygnatura': '297-1-180', 'Strona': '10R', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': 'RK', 'Indeks': '21', 'Skan': ''}
marriages_0 =  {'Dzień': '14', 'Miesiąc': '11', 'Rok': '1745', 'Parafia': 'Szumsk', 'Imię p. Młodego': 'Szymon', 'Nazwisko p. Młodego': 'Budzina', 'Skąd': 'Kąty', 'Lat': '', 'Imię Ojca': '', 'Imię Matki': '', 'Nazwisko rodowe matki': '', 'Imię p. Młodej': 'Katarzyna', 'Nazwisko p. Młodej': 'Błasczycha Błaszczuk', 'Świadkowie i uwagi': 'Józef Mediński, Marianna Medińska', 'Sygnatura': '297-1-180', 'Strona': '10V', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': 'RK', 'Indeks': '', 'Skan': ''}
deaths_0 = {'Dzień': '13', 'Miesiąc': '10', 'Rok': '1745', 'Parafia': 'Szumsk', 'Imię': 'Antoni', 'Nazwisko': 'Błasczuk Błaszczuk', 'Lat': '5', 'Miejscowość': 'Załuże', 'O zmarłym i rodzinie': 'rodzice: Jakub i Regina', 'Sygnatura': '297-1-184', 'Strona': '7V', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': '20', 'Indeks': 'RK', 'Skan': ''}
notes_0 = {'Nr Gospodarstwa': '9', 'Nr Mężczyzny': '', 'Nr Kobiety ': '', 'Personalia': 'Maciej Błaszczuk', 'Wiek Mężczyzny': '70', 'Wiek Kobiety': '', 'Parafia': 'Luboml', 'Miejscowość': 'Konty (Kąty)', 'Rok': '1791', 'Archiwum': 'Lublin', 'Spisane przez': 'BK', 'Sygnatura': '', 'Strona': '28V', 'Nr Skanu': '56', 'Uwagi 2': ''}

def translate_key(key):
    translations = {
        'Dzień': 'Day',
        'Miesiąc': 'Month',
        'Rok': 'Year',
        'Parafia': 'Parish',
        'Imiona': 'Names',
        'Nazwisko': 'Surname',
        'Miejscowość': 'Place',
        'Imię Ojca': 'Father_Name',
        'Imię Matki': 'Mother_Name',
        'Nazwisko rodowe matki': 'Mother_Maiden_Name',
        'Chrzestni i uwagi': 'Godparents_and_notes',
        'Sygnatura': 'Signature',
        'Strona': 'Page',
        'Pozycja': 'Position',
        'Archiwum': 'Archive',
        'Nr skanu': 'Scan_Number',
        'Indeks': 'Index',
        'Skan': 'Scan',
        'Imię p. Młodego': 'Groom_Name',
        'Nazwisko p. Młodego': 'Groom_Surname',
        'Skąd': 'From',
        'Lat': 'Age',
        'Imię p. Młodej': 'Bride_Name',
        'Nazwisko p. Młodej': 'Bride_Surname',
        'Świadkowie i uwagi': 'Witnesses_and_notes',
        'Imię': 'Name',
        'O zmarłym i rodzinie': 'About_the_deceased_and_family',
        'Nr Gospodarstwa': 'Household_Number',
        'Nr Mężczyzny': 'Male_Number',
        'Nr Kobiety ': 'Female_Number',
        'Personalia': 'Personal_data',
        'Wiek Mężczyzny': 'Male_Age',
        'Wiek Kobiety': 'Female_Age',
        'Spisane przez': 'Written_by',
        'Nr Skanu': 'Scan_Number',
        'Uwagi 2': 'Remarks_2'
    }
    return translations.get(key, key)

def translate_dict(data):
    return {translate_key(key): value for key, value in data.items()}


class Event(BaseModel):
    Day: str
    Month: str
    Year: str
    Parish: str
    Signature: Optional[str]
    Page: str
    Archive: str
    Scan_Number: str
    Scan: Optional[str]


class Birth(Event):
    Names: str
    Surname: str
    Place: str
    Father_Name: str
    Mother_Name: str
    Mother_Maiden_Name: Optional[str]
    Godparents_and_notes: Optional[str]
    Position: Optional[str]
    Index: Optional[str]


class Marriage(Event):
    Groom_Name: str
    Groom_Surname: str
    From: str
    Age: Optional[str]
    Father_Name: Optional[str]
    Mother_Name: Optional[str]
    Mother_Maiden_Name: Optional[str]
    Bride_Name: str
    Bride_Surname: str
    Witnesses_and_notes: Optional[str]
    Position: Optional[str]
    Index: Optional[str]


class Death(Event):
    Name: str
    Surname: str
    Age: str
    Place: str
    About_the_deceased_and_family: str
    Position: Optional[str]
    Index: str


class Note(BaseModel):
    Household_Number: str
    Male_Number: Optional[str]
    Female_Number: Optional[str]
    Personal_data: str
    Male_Age: str
    Female_Age: Optional[str]
    Parish: str
    Place: str
    Year: str
    Archive: str
    Written_by: str
    Signature: Optional[str]
    Page: str
    Scan_Number: str
    Remarks_2: Optional[str]
