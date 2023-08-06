
def fill_with_null(source_string: str, length: int, start_at_beginning: bool = True) -> str:
    return_string = ''
    if len(source_string) < length:
        if start_at_beginning:
            for _ in range(len(source_string)):
                return_string += "0"
            return_string += source_string
        else:
            return_string = source_string
            for _ in range(len(return_string)):
                return_string += "0"

    return return_string
