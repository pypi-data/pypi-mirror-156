from abc import ABC, abstractmethod


class BasisBabelSprachVersion(ABC):
    """ Basisklasse fuer die Sprachkonfigurationen """
    @abstractmethod
    def wert_fuer_code(self, code: str) -> str:
        """ Ermittelt den uebersetzten Text fuer den Code """
        pass
    pass
