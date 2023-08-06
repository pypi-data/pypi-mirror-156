import os
import string
import re
import unidecode


class Strings:
    ascii_uppercase = string.ascii_uppercase
    ascii_lowercase = string.ascii_lowercase
    ascii_letters = string.ascii_letters
    digits = string.digits
    alphanum = ascii_letters + digits
    whitespace = string.whitespace
    punctuation = string.punctuation

    @staticmethod
    def stripaccents(text: str) -> str:
        return unidecode.unidecode(text)

    @staticmethod
    def stripaccents_lower(text: str) -> str:
        return unidecode.unidecode(text).lower()

    @staticmethod
    def check_equal(str1: str, str2, *, nocase=False, noaccents=False):
        if nocase:
            str1 = str1.lower()
            str2 = str2.lower()
        if noaccents:
            str1 = Strings.stripaccents(str1)
            str2 = Strings.stripaccents(str2)
        return str1 == str2

    @staticmethod
    def to_os_linesep(text: str):
        return re.sub('[\n\r]+', os.linesep, text)

    @staticmethod
    def remove_chars(text: str, *, chars: str) -> str:
        return re.sub(f'[{re.escape(chars)}]', '', text)

    @classmethod
    def remove_extra_space_chars(cls, text: str) -> str:
        return ' '.join(text.split())

    @staticmethod
    def keep_chars(text: str, *, chars: str) -> str:
        return re.sub(f'[^{re.escape(chars)}]', '', text)

    @staticmethod
    def to_string(value, *, default=''):
        if value is None:
            return default
        try:
            if isinstance(value, bytes):
                return value.decode()
            return str(value)
        except ValueError:
            return default

    @staticmethod
    def to_int(text: str, *, default=0) -> int:
        try:
            return int(text)
        except ValueError:
            return default

    @classmethod
    def transform(cls, text: str, *, lower=False, stripaccents=False, keepchars='', removechars='') -> str:
        if lower:
            text = text.lower()
        if stripaccents:
            text = cls.stripaccents(text)
        if keepchars:
            text = cls.keep_chars(text, chars=keepchars)
        if removechars:
            text = cls.remove_chars(text, chars=removechars)
        return text
