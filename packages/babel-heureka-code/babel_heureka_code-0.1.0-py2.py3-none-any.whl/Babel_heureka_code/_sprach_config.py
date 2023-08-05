import configparser
from configparser import ConfigParser

from ._babel_basis_sprach_version import BasisBabelSprachVersion


class SprachConfig(BasisBabelSprachVersion):
    """ Verwaltet eine Sprachkonfiguration aus einer Datei """
    def __init__(self, datei, bereich: str = None):
        """
        Verwaltet eine Sprachkonfiguration aus einer Datei

        :param datei: Die zu lesende Datei
        :param bereich: Der Bereich, in dem die Codes stehen
        """
        super(SprachConfig, self).__init__()
        self._configparser = ConfigParser()
        self._configparser.read(datei, encoding="utf8")
        self.__bereich = bereich if bereich else "codes"

    def wert_fuer_code(self, code: str) -> str:
        """ Ermittelt die passende Uebersetzung """
        try:
            return self._configparser.get(self.__bereich, code)
        except configparser.NoOptionError:
            pass
        except configparser.NoSectionError:
            pass

    pass
