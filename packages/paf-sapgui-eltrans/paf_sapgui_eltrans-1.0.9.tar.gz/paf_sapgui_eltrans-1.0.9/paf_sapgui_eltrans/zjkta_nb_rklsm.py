from paf_sapgui import field


class SelectionScreen(field.Field):
    def __init__(self):
        super().__init__()

    def loader_lauf_id(self):
        self._path = "wnd[0]/usr/ctxtS_RUNID-LOW"
        return self

    def angelegt_am_von(self):
        self._path = "wnd[0]/usr/ctxtS_IMPDAT-LOW"
        return self

    def angelegt_am_bis(self):
        self._path = "wnd[0]/usr/ctxtS_IMPDAT-HIGH"
        return self

    def gruppenschluessel_ai(self):
        self._path = "wnd[0]/usr/ctxtS_AIGRP-LOW"
        return self

    def status_abo_interface(self):
        self._path = "wnd[0]/usr/ctxtS_STATUS-LOW"
        return self

    def objektnummer(self):
        self._path = "wnd[0]/usr/txtS_LDOBJ-LOW"
        return self


class Table(field.Field):
    def __init__(self):
        super().__init__()

    def tabelle(self):
        self._path = "wnd[0]/usr/cntlCC_ALV/shellcont/shell"
        return self

    def detail_tabelle(self):
        self._path = "wnd[0]/usr/cntlCC_ALV_DETAIL/shellcont/shell"
        return self
