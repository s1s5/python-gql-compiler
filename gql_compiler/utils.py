import re


def camel_case_to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()
