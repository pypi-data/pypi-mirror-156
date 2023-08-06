from paf_sapgui import field


class Fenster(field.Field):
    def quelldatei_auf_applikationsserver(self):
        self._path = "wnd[1]/usr/txtRCGFILETR-FTAPPL"
        return self

    def zieldatei_auf_frontend(self):
        self._path = "wnd[1]/usr/ctxtRCGFILETR-FTFRONT"
        return self

    def datei_ueberschreiben(self):
        self._path = "wnd[1]/usr/chkRCGFILETR-IEFOW"
        return self

    def herunterladen(self):
        self._path = "wnd[1]/tbar[0]/btn[13]"
        return self

    def abbruch(self):
        self._path = "wnd[1]/tbar[0]/btn[12]"
        return self

    def abbrechen(self):
        self._path = None
        return self
