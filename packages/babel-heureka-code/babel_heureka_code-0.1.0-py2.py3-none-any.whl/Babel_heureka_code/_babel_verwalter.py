from logging import getLogger

import Babel_heureka_code._babel_code as _babel_code

from ._babel_basis_sprach_version import BasisBabelSprachVersion
from ._babel_basis_verwalter import BabelBasisVerwalter
from .exceptions import (InkompatibleSprache, KeineSpracheGesetzt,
                         UnbekannterCode)


class BabelVerwalter(BabelBasisVerwalter):
    """ Verwaltet verschiedene Referenzen """
    def __init__(self, sprache: BasisBabelSprachVersion = None, logger=None):
        """
        Verwaltet verschiedene Referenzen

        :param sprache: Die aktuelle Sprache
        """
        self.__registrierte_codes = set()
        self.__logger = logger if logger else getLogger(__name__)
        self.__sprache = None
        if sprache is not None:
            self.setze_sprache(sprache)

    def __call__(self, code):
        """
        Erstellt eine neue Referenz

        :param code: Der Name der zu erstellenden Referenz
        :return: Der Erstellte BabelCode
        """
        obj = _babel_code.BabelCode(code)
        obj.verwalter_setzen(self)
        return obj

    def setze_sprache(self, sprache: BasisBabelSprachVersion):
        """
        Setzt die aktuell zu verwendende Sprache

        :param sprache: Die zu verwendende Sprache
        :rtype InkompatibleSprache: Wenn keine Instanz von BasisBabelSprachVersion genutzt wird
        :return: None
        """
        if not isinstance(sprache, BasisBabelSprachVersion):
            raise InkompatibleSprache(sprache)
        self.__sprache = sprache
        for code in self.undefinierte_codes:
            self.__logger.critical(f"{sprache} definiert {code} nicht")

    @property
    def undefinierte_codes(self) -> list[str]:
        """
        Liefert die Codes, die fuer die aktuelle Sprache nicht gesetzt sind

        :return: Die undefinierten Codes
        :rtype: list[str]
        """
        if self.__sprache is None:
            return list(self.__registrierte_codes)
        undef = []
        for code in self.__registrierte_codes:
            try:
                wert = self.__sprache.wert_fuer_code(code)
                if wert is None:
                    raise UnbekannterCode(code)
            except UnbekannterCode:
                undef.append(code)
        undef.sort()
        return undef

    def wert_fuer_code(self, code: str) -> str:
        """
        Ermittelt den Wert fuer einen gegebenen Code

        :param code: Der abgefragte Code
        :return: Der aktuelle Wert
        """
        if not self.ist_code_registriert(code):
            self.code_registrieren(code)
        if self.__sprache is None:
            raise KeineSpracheGesetzt()
        wert = self.__sprache.wert_fuer_code(code)
        if wert is None:
            raise UnbekannterCode(code)
        return wert

    def code_registrieren(self, code_name: str) -> None:
        """
        Registriert einen Code

        :param code_name: Der Name des zu registrierenden Codes
        :return: None
        """
        self.__registrierte_codes.add(code_name)

    def ist_code_registriert(self, code_name: str) -> bool:
        """
        Prueft, ob ein Code registriert ist

        :param code_name: Der Name der Referenz
        :return: Ob der Code existiert
        :rtype: bool
        """
        return code_name in self.__registrierte_codes

    def __repr__(self):
        """ Die Darstellung des Verwalters """
        return f"<{self.__class__.__name__} {len(self.__registrierte_codes)} registrierte Codes>"
    pass
