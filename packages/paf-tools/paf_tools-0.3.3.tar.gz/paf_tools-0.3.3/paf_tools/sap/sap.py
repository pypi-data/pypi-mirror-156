from paf_tool_generators import name, address


def create_firstname_lastname():
    firstname, lastname, gender = name.create_firstname_lastname()
    gender_number = 0
    if gender == "company":
        gender_number = 5
    elif gender == "family":
        gender_number = 6
    elif gender == "female":
        gender_number = 3
    elif gender == "female_male":
        gender_number = 28
    elif gender == "male":
        gender_number = 2
    elif gender in {"divers", "neutral"}:
        gender_number = 4

    return firstname, lastname, gender, gender_number


def create_address():
    return address.create()
