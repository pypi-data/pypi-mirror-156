from random import random


def __get_data(data_name):
    imported_file = __import__(f'data/names/{data_name}')
    return getattr(imported_file, 'return_data')


def create_gender() -> str | None:
    try:
        genders = ["male", "female", "company", "divers", "family", "female_male"]
        return genders[random.randint(0, len(genders) - 1)]
    except Exception as ex:
        print(ex)
        return None


def create_lastname() -> str:
    lastnames = __get_data('lastnames')

    return lastnames[random.randint(0, len(lastnames) - 1)]


def create_firstname(gender: str = None) -> str:
    gender = gender.lower()

    if gender == "male":
        return create_firstname_male()
    if gender == "female":
        return create_firstname_female()
    if gender is None:
        return create_firstname_male() if random.randint(2, 3) == 2 else create_firstname_female()
    if gender in {"company", "divers", "family"}:
        return ''
    if gender == "female_male":
        return f'{create_firstname_female()} / {create_firstname_male()}'


def get_salutation_for_gender(gender: str) -> str:
    gender = gender.lower()

    if gender == "male":
        return "Mister"
    if gender == "female":
        return "Miss"
    if gender == "female_male":
        return "Miss / Mister"
    if gender == "company":
        return "Company"
    if gender == "family":
        return "Family"

    return ""


def create_firstname_female():
    firstnames = __get_data('firstnames_female')

    return firstnames[random.randint(0, len(firstnames) - 1)]


def create_firstname_male():
    vornamen = __get_data('firstname_male')

    return vornamen[random.randint(0, len(vornamen) - 1)]


def create_firstname_random():
    if random.randint(2, 3) == 2:
        # Vorname, Geschlecht
        return create_firstname_male(), 'male'
    else:
        return create_firstname_female(), 'female'


# -------------------- Namen - Gesamt
def create_full_name():
    return create_firstname_lastname()


def create_firstname_lastname():
    local_gender = create_gender()
    local_firstname = None

    if local_gender == "male":
        local_firstname = create_firstname_male()
    if local_gender == "female":
        local_firstname = create_firstname_female()
    if local_gender == "divers":
        local_firstname = 'neutral'
    if local_gender == "company":
        local_firstname = ''
    if local_gender == "family":
        local_firstname = ''
    if local_gender == "female_male":
        local_firstname = f'{create_firstname_female()} {create_firstname_male()}'

    # Vorname, Nachname, Geschlecht
    return local_firstname, create_lastname(), local_gender


def create_firstname_female_lastname():
    # Geschlecht, Vorname, Nachname
    return create_firstname_female(), create_lastname(), 'female'


def create_firstname_male_lastname():
    # Geschlecht, Vorname, Nachname
    return create_firstname_male(), create_lastname(), 'male'
