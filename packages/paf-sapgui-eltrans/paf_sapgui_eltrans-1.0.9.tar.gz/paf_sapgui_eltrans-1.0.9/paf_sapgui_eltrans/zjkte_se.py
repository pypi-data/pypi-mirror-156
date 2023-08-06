from enum import Enum


def set_fieldtype(field: str, field_type):
    return field.replace("[FIELDTYPE]", field_type.value)


class OptInDialog:
    kanal = "wnd[1]/usr/lblZJGT_OPTIN-EVEKANAL"
    einholdatum = "wnd[1]/usr/ctxtZJGT_OPTIN-EINHOLDATUM"
    generelles_opt_in = "wnd[1]/usr/radGV_GOI"
    generelles_opt_out = "wnd[1]/usr/radGV_GOO"


class Tabs(Enum):
    auftraggeber = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1"
    warenempfaenger = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC2"
    vermittler = ""


class NameAndAddresstypes(Enum):
    auftraggeber = "0201",
    warenempfaenger = "0202",
    vermittler = ""


class SelectionScreen:
    werbeaktion = "wnd[0]/usr/ctxtTJWAK-WERBEAKT"
    kampagnen_id = "wnd[0]/usr/ctxtZJKT_KID-KID"
    splitkezi = "wnd[0]/usr/ctxtJKAP-ZZ_KEZI_SPLIT"


class Basics:
    werb_aktion = ""
    kid = ""
    bz_dr_erz = ""
    pva = ""
    bez_typ = ""
    a_art = ""
    p_art = ""


class Vermittler:
    @staticmethod
    def select_tab():
        asit_tabs.select_tab(tabs.vermittler)


class Warenempfaenger:
    @staticmethod
    def select_tab():
        asit_tabs.select_tab(tabs.warenempfaenger)


class Auftraggeber:
    class Basisdaten:
        anrede = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:0201/ctxtZJGS_AI_BP-ANRED"
        details = ""
        geschaeftspartner = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/ctxtZJGS_AI_BP-GPNR"
        nachname_firma_1 = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-NAME1"
        vorname_firma_2 = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-NAME2"
        zus_1_abteilung = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-NAME3"
        zus_2_ansprechpartner = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-NAME4"
        strasse = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-STRAS"
        nr = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-HAUSN"
        erg = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-HSNMR2"
        plz = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-PSTLZ"
        ort = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:0201/txtZJGS_AI_BP-ORT01"
        ortsteil = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-ORT02"
        postfach = ""
        land_fuer_aufbereitung = ""
        zugabe_1 = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/ctxtZJKS_AI_ORDER-ZUGABE1"
        zugabe_2 = ""
        zugabe_3 = ""
        ersatzzugabe_1 = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/ctxtZJKS_AI_ORDER-EZUGABE1"
        ersatzzugabe_2 = ""
        ersatzzugabe_3 = ""
        IBAN = "wnd[0]/usr/tabsGP_TAB/tabpGP_TAB_FC1/ssubGP_TAB_SCA:SAPMZJK_SE:[FIELDTYPE]/txtZJGS_AI_BP-ZZIBAN"
        BIC = ""
        bankschl = ""
        bankkto = ""
        bankland = ""
        kartennummer_ccv = ""
        gueltig_bis = ""
        kartenart = ""


class Faktura:
    fak_per = ""
    fak_term = "wnd[0]/usr/ctxtZJKS_AI_ORDER-FAKTERM"
    zahlweg = ""
    rech_druck_bankeinzug = ""


class Auftrag:
    termintyp = "wnd[0]/usr/ctxtZJKS_AI_ORDER-TERMINTYP"
    zeitraum_von = "wnd[0]/usr/txtZJKS_AI_ORDER-TERMVON"
    zeitraum_bis = "wnd[0]/usr/txtZJKS_AI_ORDER-TERMBIS"
    lf_ende_grd = "wnd[0]/usr/ctxtZJKS_AI_ORDER-LIEFEREND"
    bestellart = "wnd[0]/usr/ctxtZJKS_AI_ORDER-BSARK"
    adr_quelle = ""
    menge = ""
    bestelldat = "wnd[0]/usr/ctxtZJKS_AI_ORDER-BSTDK"
    bestell_nr_gk = ""
    werbender_ash = ""
    splitkezi = ""
    box_id = ""
    agenturwerber = ""


class Zusaetzliche_Daten:
    lf_hinweise = ""
    lieferart = ""
    bezugsperiod = ""
    vertr_konto = ""
    druck_we = ""
    anzahl = ""
    medium = ""
    druck = ""
    referenzbeleg = ""
