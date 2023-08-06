import re
import enum
import requests
from typing import Tuple

NAMES_REGEX = r'<textarea id="result_textarea".*?>(.+)</textarea>'


class NameType(enum.IntEnum):
    full = 0
    surname_firstname = 1
    firstname_surname = 2
    surname_initials = 3
    initials_surname = 4
    name = 5
    surname_firstname_eng = 101


class Sex(enum.IntEnum):
    any = 10
    male = 0
    female = 1


def generate_names(
        count: int = 10,
        nametype: NameType = NameType.full,
        sex: Sex = Sex.any) -> Tuple[str, ...]:

    resp = requests.get(
        'https://randomus.ru/name',
        params={
            'type': nametype,
            'sex': sex,
            'count': count
        }
    )
    resp.raise_for_status()

    names = re.search(NAMES_REGEX, resp.text, re.DOTALL)
    if names is None:
        raise LookupError(
            'Не удалось извлечь имена из HTML-ответа'
        )

    lst = names.group(1).replace('\r\n', '\n').split('\n')
    return tuple(lst)
