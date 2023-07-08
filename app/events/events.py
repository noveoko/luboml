from pydantic import BaseModel


births_0 =  {'Dzień': '13', 'Miesiąc': '6', 'Rok': '1741', 'Parafia': 'Szumsk', 'Imiona': 'Antoni', 'Nazwisko': 'Błaszczuk', 'Miejscowość': 'Załuże', 'Imię Ojca': 'Jakub', 'Imię Matki': 'Regina', 'Nazwisko rodowe matki': '', 'Chrzestni i uwagi': 'Tomasz Rarzebiński, Jadwiga Franczycha', 'Sygnatura': '297-1-180', 'Strona': '10R', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': 'RK', 'Indeks': '21', 'Skan': ''}
marriages_0 =  {'Dzień': '14', 'Miesiąc': '11', 'Rok': '1745', 'Parafia': 'Szumsk', 'Imię p. Młodego': 'Szymon', 'Nazwisko p. Młodego': 'Budzina', 'Skąd': 'Kąty', 'Lat': '', 'Imię Ojca': '', 'Imię Matki': '', 'Nazwisko rodowe matki': '', 'Imię p. Młodej': 'Katarzyna', 'Nazwisko p. Młodej': 'Błasczycha Błaszczuk', 'Świadkowie i uwagi': 'Józef Mediński, Marianna Medińska', 'Sygnatura': '297-1-180', 'Strona': '10V', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': 'RK', 'Indeks': '', 'Skan': ''}
deaths_0 = {'Dzień': '13', 'Miesiąc': '10', 'Rok': '1745', 'Parafia': 'Szumsk', 'Imię': 'Antoni', 'Nazwisko': 'Błasczuk Błaszczuk', 'Lat': '5', 'Miejscowość': 'Załuże', 'O zmarłym i rodzinie': 'rodzice: Jakub i Regina', 'Sygnatura': '297-1-184', 'Strona': '7V', 'Pozycja': '', 'Archiwum': 'Ł', 'Nr skanu': '20', 'Indeks': 'RK', 'Skan': ''}
notes_0 = {'Nr Gospodarstwa': '9', 'Nr Mężczyzny': '', 'Nr Kobiety ': '', 'Personalia': 'Maciej Błaszczuk', 'Wiek Mężczyzny': '70', 'Wiek Kobiety': '', 'Parafia': 'Luboml', 'Miejscowość': 'Konty (Kąty)', 'Rok': '1791', 'Archiwum': 'Lublin', 'Spisane przez': 'BK', 'Sygnatura': '', 'Strona': '28V', 'Nr Skanu': '56', 'Uwagi 2': ''}



class Event(BaseModel):
    date: str


class Marriage(Event):
    pass

class Death(Event):
    pass

class Birth(Event):
    pass

class Note(Event):
    pass


x = Event(date='02/11/2023')
m = Marriage(date='03/21/2022')