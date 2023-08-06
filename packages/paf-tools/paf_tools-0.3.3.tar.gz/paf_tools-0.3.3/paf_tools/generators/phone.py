# -------------------- Phone
# -------------------- Phone - Parts
from random import random


def mobil_vorwahl(format_return_value=False):
    return vorwahl(True, format_return_value)


def festnetz_vorwahl(format_return_value=False):
    return vorwahl(False, format_return_value)


def mobil_nummer(format_return_value=False):
    return number(True, format_return_value)


def festnetz_nummer(format_return_value=False):
    return number(False, format_return_value)


def vorwahl(is_mobile=False, format_return_value=False):
    try:
        return_value = ''
        if is_mobile:
            return_value = "01"
            for _ in range(2):
                return_value += random.randint(1, 9)

            if format_return_value:
                return_value = f"({return_value[1:1]} {return_value[2:2]})"
        else:
            return_value = "0"
            for _ in range(4):
                return_value += random.randint(1, 9)

            if format_return_value:
                return_value = f"({return_value[1:1]} {return_value[2:3]}) {return_value[3:5]})"

            return return_value
    except Exception as ex:
        print(ex)
        return None


def number(is_mobile=False, format_return_value=False):
    try:
        number_value = ""
        number_length = 6
        if is_mobile:
            number_length = 9

        for _ in range(number_length):
            number_value += random.randint(1, 9)

        if format_return_value:
            if is_mobile:
                return number_value.Substring(0, 2) + " " + number_value.Substring(2, 2) + " " + number_value.Substring(
                    4, 2) + " " + number_value.Substring(6)
            else:
                return number_value.Substring(0, 2) + " " + number_value.Substring(2, 2) + " " + number_value.Substring(
                    4, 2)
        return number_value
    except Exception as ex:
        print(ex)
        # Logging_old.WriteLogError(ex.Message)
        return None


# -------------------- Telefon - Gesamt

def mobil(format_return_value=False):
    if format_return_value:
        return f"{mobil_vorwahl(format_return_value)} - {mobil_nummer(format_return_value)}"
    else:
        return f"{mobil_vorwahl(format_return_value)} {mobil_nummer(format_return_value)}"


def festnetz(format_return_value=False):
    if format_return_value:
        return f"{festnetz_vorwahl(format_return_value)} - {festnetz_nummer(format_return_value)}"
    else:
        return f"{festnetz_vorwahl(format_return_value)} {festnetz_nummer(format_return_value)}"
