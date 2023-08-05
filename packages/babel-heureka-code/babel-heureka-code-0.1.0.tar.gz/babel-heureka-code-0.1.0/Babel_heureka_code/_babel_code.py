import Babel_heureka_code._babel_basis_verwalter as _babel_basis_verwalter

from ._babel_code_meta import BabelCodeMeta
from .exceptions import InkompatiblerVerwalter


class BabelCode(metaclass=BabelCodeMeta):
    """ Klasse zur Referenzierung einer Sprachversion """
    def __init__(self, name: str):
        """
        Klasse zur Referenzierung einer Sprachversion

        :param name: Der Name der Referenz
        """
        self.__name: str = name
        self.__verwalter = None

    def verwalter_setzen(self, verwalter: "_babel_basis_verwalter.BabelBasisVerwalter"):
        """
        Setzt den Verwalter der Referenz

        :param verwalter: Der zu setzende Verwalter
        :raise InkompatiblerVerwalter: Wenn keine Instanz von BabelBasisVerwalter genutzt wird
        :return: None
        """
        if isinstance(verwalter, _babel_basis_verwalter.BabelBasisVerwalter):
            self.__verwalter = verwalter
            self.__verwalter.code_registrieren(self.name)
        else:
            raise InkompatiblerVerwalter(verwalter)
        pass

    def __str__(self):
        """ Der aktuell referenzierte Wert """
        if self.__verwalter:
            return self.wert
        return f"<undefinierter BabelCode {self.name}>"

    def __repr__(self):
        """ Die Darstellung der Referenz """
        return f"<BabelCode {self.name}>"

    def __eq__(self, other):
        """ Prueft, ob zwei Referenzen gleich sind """
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        """ Prueft, ob zwei Referenzen gleich sind """
        return not (self == other)

    @property
    def wert(self) -> [str, None]:
        """ Der aktuell referenzierte Wert """
        if self.__verwalter:
            return self.__verwalter.wert_fuer_code(self.name)
        return None

    @property
    def name(self) -> str:
        """ Der verwendete Codename """
        return self.__name
