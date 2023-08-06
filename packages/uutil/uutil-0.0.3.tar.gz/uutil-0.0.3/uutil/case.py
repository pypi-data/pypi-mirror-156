# coding: utf-8
import re

class CaseUtil:

    @classmethod
    def camel_to_snake(cls, s: str):
        """ camel case to snake case """
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    @classmethod
    def snake_to_camel(cls, s: str):
        """ snake case to camel case """
        return ''.join(it.title() for it in s.split('_'))
