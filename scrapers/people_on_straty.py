from bs4 import BeautifulSoup as bs

raw_page = None
with open('/content/<straty_people_result.html>') as page:
  raw_page = page.read()
  
# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Structure to hold extracted data
persons_data = []

# Assuming that the first input with class 'tekst_szukaj_wynik_lp' indicates a new row
for input_lp in soup.find_all('input', class_='tekst_szukaj_wynik_lp'):
    person_data = {}
    # The following sibling inputs should contain the data for the current row
    inputs = input_lp.find_next_siblings('input', class_='tekst_szukaj_wynik_lista')

    if inputs:
        fields = ['Nazwisko', 'Imię', 'Nazwisko panieńskie', 'Data urodzenia', 'Miejsce urodzenia', 'Imię ojca', 'Imię matki', 'Data śmierci']
        for field, input_element in zip(fields, inputs):
            person_data[field] = input_element.get('value', '').strip()

        persons_data.append(person_data)

# Print extracted data
for person in persons_data:
    print(person)
