from paf_sapgui import field

auftragstabs = r"wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP"
auftragsschaltflaechen = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/cntlCONT_MSD_ORDER_0100/shellcont/shell"
tabs = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP"
hitliste = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB2/ssubSUB_TAB:SAPLCRM_CIC_NAV_AREA:1003/cntlNAV_CUST_CONT/shellcont/shell"
auftragstabelle = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/cntlCONT_MSD_ORDER_0100/shellcont/shell"
reklatabelle = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB7/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLZJCFU_03_REKLAM:0100/cntlGV_ALV_0100_REKL_CONT/shellcont/shell"


class Geschaeftspartner(field.Field):
    def manuelle_identifikation(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnCONTINUE_BUTTON"
        return self

    def suchen(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnSEARCH_BUTTON"
        return self

    def anzeigen(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnDISPLAY_BUTTON"
        return self

    def anlegen(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnCREATE_BUTTON"
        return self

    def adressaenderung(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnG_BUT_ADDRESS_CHANGE"
        return self

    def alle_felder_initialisieren(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/btnDELETE_BUTTON"
        return self

    def name_1(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-NAME1"
        return self

    def name_2(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-NAME2"
        return self

    def strasse(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-STRAS"
        return self

    def hausnummer(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-HAUSN"
        return self

    def hausnummer_zusatz(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-HSNMR2"
        return self

    def plz(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-PSTLZ"
        return self

    def ort(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-ORT01"
        return self

    def land(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/ctxtRJYCIC_SEARCH-LAND1"
        return self

    def gp_nummer(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/ctxtRJYCIC_SEARCH-GPNR"
        return self

    def telefon(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-ANI_TELNR"
        return self

    def art_der_suche(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/cmbRJYCIC_SEARCH-DOCUMENT_TYPE"
        return self

    def suchdaten(self):
        self._path = "wnd[0]/usr/ssubAREA01:SAPLCCM1:8100/subCONTACT_DISPLAY:SAPLJYCIC_SEARCH:0010/subISM_CIC_SEARCH:SAPLJYCIC_SEARCH:0105/txtRJYCIC_SEARCH-DOCUMENT"
        return self


class Suchergebnisse(field.Field):
    class Tabs(field.Field):
        def tabs(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP"
            return self

        def umfeld(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB1"
            return self

        def hitliste(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB2"
            return self

        def scripting(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB3"
            return self

        def zwischenablage(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB4"
            return self

    class Umfeld(field.Field):
        def auffrischen(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB1/ssubSUB_TAB:SAPLCRM_CIC_NAV_AREA:1002/subSUB_BUT:SAPLCRM_CIC_NAV_AREA:1009/btnNA_BUT1"
            return self

        def tabelle(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB1/ssubSUB_TAB:SAPLCRM_CIC_NAV_AREA:1002/cntlNAV_CUST_CONT/shellcont/shell"
            return self

    class Hitliste(field.Field):
        def tabelle(self):
            self._path = "wnd[0]/usr/ssubAREA05:SAPLCRM_CIC_NAV_AREA:1001/tabsTABSTRIP/tabpNA_TAB2/ssubSUB_TAB:SAPLCRM_CIC_NAV_AREA:1003/cntlNAV_CUST_CONT/shellcont/shell"
            return self


class Auftraege(field.Field):
    class Tabs(field.Field):
        def msd_auftraege(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1"
            return self

        def praemien(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB2"
            return self

        def faktura_mca(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB3"
            return self

        def word(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB4"
            return self

        def kontaktbearbeitung(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB5"
            return self

        def kontakthistorie(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB6"
            return self

        def reklamation(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB7"
            return self

        def digitale_auftraege(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB8"
            return self

    class MsdAuftraege(field.Field):
        def details_zur_position_anzeigen(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/btnBUTTON_ORDERLIST_VIEW"
            return self

        def auffrischen(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/btnBUTTON_ORDERLIST_REFRESH"
            return self

        def alle_felder_initialisieren(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/btnBUTT_SDEL"
            return self

        def tabelle(self):
            self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0100/cntlCONT_MSD_ORDER_0100/shellcont/shell"
            return self

    class DetailsZurPosition(field.Field):
        class Tabs(field.Field):
            def tabs(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP"
                return self

            def details_zur_position(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB1"
                return self

            def fakturen(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB1"
                return self

            def vertriebsunterstuetzung(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB3"
                return self

            def partner_anschriften(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB4"
                return self

            def text(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB5"
                return self

            def flexibler_preiswechsel(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB6"
                return self

        class Text(field.Field):
            def anzeigen_aendern(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB5/ssubSUB_TAB:SAPLJCCM21:0105/ssubCCM21_CUST_SUB:SAPLZJCFU_MSDORDERDETAIL:0120/btnTOGGLE_DISPLAY"
                return self

            def sichern(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB5/ssubSUB_TAB:SAPLJCCM21:0105/ssubCCM21_CUST_SUB:SAPLZJCFU_MSDORDERDETAIL:0120/btnSAVE_TEXT"
                return self

            def text_element(self):
                self._path = "wnd[0]/usr/ssubAREA06:SAPLCCM21:1001/tabsTABSTRIP/tabpAA_TAB1/ssubSUB_TAB:SAPLCCM21:1005/ssubCCM21_CUST_SUB:SAPLJYCIC_MSDORDER:0110/subAPPL:SAPLJCCM21:0101/tabsTABSTRIP/tabpSD_TAB5/ssubSUB_TAB:SAPLJCCM21:0105/ssubCCM21_CUST_SUB:SAPLZJCFU_MSDORDERDETAIL:0120/cntlTEXT_ORDER_ITEM/shellcont/shell"
                return self
