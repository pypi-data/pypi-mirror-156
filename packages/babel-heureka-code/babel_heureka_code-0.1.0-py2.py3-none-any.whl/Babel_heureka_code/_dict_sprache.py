from ._babel_basis_sprach_version import BasisBabelSprachVersion


class DictSprache(BasisBabelSprachVersion):
    """ Erstellt eine Sprachkonfiguration im Code """
    def __init__(self, dic: dict = None, **kwargs):
        """ Erstellt eine Sprachkonfiguration im Code """
        super(DictSprache, self).__init__()
        self.__werte = dic if dic else {}
        for key, value in kwargs.items():
            self.__werte[key] = value

    def wert_fuer_code(self, code: str) -> str:
        """ Ermittelt den referenzierten Wert """
        return self.__werte.get(code, None)
    pass
