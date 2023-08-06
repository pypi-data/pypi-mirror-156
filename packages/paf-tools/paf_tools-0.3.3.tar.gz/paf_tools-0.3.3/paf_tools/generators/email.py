from random import random

from paf_tools import text


def __get_data(data_name: str):
    imported_file = __import__(f'data/email/{data_name}')
    return getattr(imported_file, "return_data")


def email() -> str:
    return f'{text.lorem_impsum()}.{text.lorem_impsum()}@{email_provider()}'


def email_provider() -> str:
    email_providers = __get_data('providers')
    return email_providers[random.randint(0, len(email_providers)-1)]


def email_address_from_name(first_name: str, last_name: str) -> str | None:
    try:
        address = ''
        if not first_name and not last_name:
            return f'no.name@{email_provider()}'

        if first_name != '' and last_name != '':
            address = f'{first_name.lower()}.{last_name.lower()}@{email_provider()}'
        if first_name != '' and not last_name:
            address = f'{first_name.lower()}@{email_provider()}'
        if not first_name and last_name != '':
            address = f'{last_name.lower()}@{email_provider()}'
        return text.check_string(address)
    except Exception as ex:
        print(ex)
        return None
