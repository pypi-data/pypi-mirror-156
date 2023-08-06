from . import general


def check_string(email_address: str) -> str:
    email_address = email_address.replace(" ", "-")
    email_address = general.replace_umlauts(email_address)
    return email_address
