from random import random


def __get_data(data_name):
    imported_file = __import__(f'data/addresses/{data_name}')
    return getattr(imported_file, "return_data")


def create_street(in_which_city):
    streets = __get_data(in_which_city.lower())

    value = streets[random.randint(1, streets.Length)]
    values = value.Split("__")
    # Strasse, Postleitzahl
    return values[0], values[1]


def create_house_number():
    return random.randint(1, 300)


def create_city():
    cities_file = __import__('addresses/cities')
    cities = getattr(cities_file, "cities")

    return cities[random.randint(0, len(cities) - 1)]


# -------------------- Ort - Gesamt
def create():
    city = create_city()
    street, zip_code = create_street(city)
    # Strasse, Hausnummer, PLZ, Ort
    return street, create_house_number(), zip_code, city
