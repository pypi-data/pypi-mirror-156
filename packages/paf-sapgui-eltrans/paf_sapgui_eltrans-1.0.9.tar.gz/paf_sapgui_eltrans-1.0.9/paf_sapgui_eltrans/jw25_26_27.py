from enum import Enum

tableiste = "wnd[0]/usr/tabsWERBEAKTION"


class SelectionScreen:
    werbeaktion = "wnd[0]/usr/lblTJWAK-WERBEAKT"


class Faktura:
    Zahlweg = "wnd[0]/usr/tabsWERBEAKTION/tabpZ9FA/ssubSUBAREA:SAPMJWAK:9003/ctxtTJWAK-ZZ_ZAHLWEG"


class Tabs(Enum):
    werbeerfolg = "tabpQUOT",
    druckerzeugnis = "tabpPUBL",
    auftrag = "tabpZ9OR",
    praemie = "tabpZ9PR",
    werbeaktionsgruppe = "tabpZ9WG",
    faktura = "tabpZ9FA",
    preiswechsel = "tabpZ9PW"
