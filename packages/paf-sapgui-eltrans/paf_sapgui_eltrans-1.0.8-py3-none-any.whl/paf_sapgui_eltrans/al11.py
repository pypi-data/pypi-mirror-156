from paf_sapgui import field


class Table(field.Field):
    def table(self):
        self._path = "wnd[0]/usr/cntlGRID1/shellcont/shell"
        return self
