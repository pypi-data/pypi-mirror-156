from abc import ABC, abstractmethod

from ._babel_basis_sprach_version import BasisBabelSprachVersion
from ._babel_code import BabelCode


class BabelBasisVerwalter(ABC):
    """ Basisklasse fuer den Verwalter """
    @abstractmethod
    def __call__(self, code):
        """ Erstellt einen neuen Code """
        pass

    @abstractmethod
    def setze_sprache(self, sprache: BasisBabelSprachVersion):
        """ Setzt die aktuelle Sprache des Verwalters """
        pass

    @abstractmethod
    def wert_fuer_code(self, code: str) -> str:
        """ Ermittelt den Wert fuer einen gegebenen Code """
        pass

    @abstractmethod
    def code_registrieren(self, code_name: str) -> None:
        """ Registriert den Code dem Verwalter """
        pass

    @abstractmethod
    def ist_code_registriert(self, code_name: str) -> bool:
        """ Prueft, ob ein Code registriert ist """
        pass

    def __getattr__(self, item):
        """ Erstellt einen neuen Code """
        if item in self.__dict__:
            return super(BabelBasisVerwalter, self).__getattr__(item)
        return self(item)

    def __repr__(self):
        """ Stellt einen Verwalter dar """
        return f"<{self.__class__.__name__} {len(self.__registrierte_codes)} registrierte Codes>"
    pass
