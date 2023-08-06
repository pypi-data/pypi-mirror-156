from paf_sapgui import field


class Table(field.Field):
    def table(self):
        self._path = "wnd[0]/usr/cntlCUCO1/shellcont/shell"
        return self


class SelectionScreen(field.Field):
    def status_des_rai(self):
        self._path = "wnd[0]/usr/ctxtS_STATUS-LOW"
        return self

    def belegart(self):
        self._path = "wnd[0]/usr/ctxtS_BELART-LOW"
        return self

    def zaehlen(self):
        self._path = "wnd[0]/usr/btnP_BUTTON"
        return self

    def datum_von(self):
        self._path = "wnd[0]/usr/ctxtS_DATUM-LOW"
        return self

    def datum_bis(self):
        self._path = "wnd[0]/usr/ctxtS_DATUM-HIGH"
        return self

    def ausfuehren(self):
        self._path = "wnd[0]/tbar[1]/btn[8]"
        return self
