class BabelCodeMeta(type):
    """ Metaklasse fuer BabelCode """

    def __getattr__(cls, item):
        """ Erstellt eine neue Referenz ueber Attribut-Syntax """
        return cls(item)
