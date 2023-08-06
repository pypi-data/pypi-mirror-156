from enum import Enum

class Tabs(Enum):
    grunddaten = "tabpFC1",
    sachpraemien = "tabpFC2",
    werbetraeger = "tabpFC4"
    ereignisse = "tabpFC5"


class SelectionScreen:
    Verkaufsorganisation = "wnd[0]/usr/subSUB100:SAPMJW34:0102/ctxtJWBASI-VKORG"
    Vertriebsweg = "wnd[0]/usr/tabsWERBEAKTION"
    Sparte = "wnd[0]/usr/subSUB100:SAPMJW34:0102/ctxtJWBASI-SPART"
    Werbeart = "wnd[0]/usr/subSUB100:SAPMJW34:0102/ctxtJWBASI-WERBEART"
    Werbeaktion = "wnd[0]/usr/subSUB100:SAPMJW34:0102/ctxtJWBASI-WERBEAKT"
    Beginn_Werbebasis = "wnd[0]/usr/subSUB100:SAPMJW34:0102/ctxtJWBASI-GUELTIGVON"


class Werbetraeger:
        Werbetraeger=f"wnd[0]/usr/tabsVERTRIEBSUNT/{Tabs.werbetraeger}"


class Sachpraemien:
        sachpraemien=f"wnd[0]/usr/tabsVERTRIEBSUNT/{Tabs.sachpraemien}"

    def get_zugaben():
        row_counter = 0
        bonus_items = []
        try:
            local_cell = sessions.sessions.findById(
                f"wnd[0]/usr/tabsVERTRIEBSUNT/tabpFC2/ssubSUBAREA:SAPMJW34:0302/tblSAPMJW34PRAEMIE/ctxtJWSAPR-MATNR[4,{row_counter}]")
            bonus_items.append(local_cell._text)
        except Exception as ex:
            return bonus_items

        return bonus_items



