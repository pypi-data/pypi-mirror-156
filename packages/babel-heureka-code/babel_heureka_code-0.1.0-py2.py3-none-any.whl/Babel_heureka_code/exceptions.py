class BabelException(Exception):
    """ Basisklasse fuer die verwendeten Exceptions """


class InkompatiblerVerwalter(BabelException):
    """ Wird ausgeloest, wenn ein unerlaubtes Objekt als Verwalter uebergeben werden soll """


class InkompatibleSprache(BabelException):
    """ Wird ausgeloest, wenn ein unerlaubtes Objekt als Sprache uebergeben werden soll """


class UnbekannterCode(BabelException):
    """ Wird ausgeloest, wenn ein unbekannter Code referenziert wird """


class KeineSpracheGesetzt(BabelException):
    """ Wird ausgeloest, wenn keine Sprache gesetzt wurde """
