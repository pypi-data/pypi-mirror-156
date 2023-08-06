//namespace AS.Auto.Web.Sap.Gui.Elemente.Vx.Transaktionen
//{
//  using OpenQA.Selenium;
//  using aliasElements = As.It.Ses.Frameworks.Selenium.Sap.Gui.Selection.Elements;

//  public static class Sm37
//    {
//        public static class Einfache_Jobauswahl
//        {
//            public static class Editfelder
//            {
//                public static IWebElement Jobname(int windowId = 0)
//                {
//                    return aliasElements.CreateElement("wnd[" + windowId + "]/usr/txtBTCH2170-JOBNAME", true);
//                }

//                public static IWebElement Benutzername(int FensterID = 0) { return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/txtBTCH2170-USERNAME", true); }
//            }

//            public static class Jobstartbedingungen
//            {
//                public static class Editfelder
//                {
//                    public static IWebElement Datum_von(int FensterID = 0) { return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/ctxtBTCH2170-FROM_DATE", true); }
//                    public static IWebElement Datum_bis(int FensterID = 0)
//                    {
//                        return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/ctxtBTCH2170-TO_DATE", true);
//                    }
//                    public static IWebElement Uhrzeit_von(int FensterID = 0)
//                    {
//                        return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/ctxtBTCH2170-FROM_TIME", true);
//                    }
//                    public static IWebElement Uhrzeit_bis(int FensterID = 0)
//                    {
//                        return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/ctxtBTCH2170-TO_TIME", true);
//                    }
//                    public static IWebElement Ereignis(int FensterID = 0)
//                    {
//                        return aliasElements.CreateElement("wnd[" + FensterID + "]/usr/cmbBTCH2170-EVENTID", true);
//                    }
//                }
//            }
//        }
//        public static class Ausgabesteuerung_Uebersicht_der_Spool_Auftraege
//        {
//            public static class Tabelle
//            {

//                const int ROWS = 2;

//                public static IWebElement Spool_Nr(int row, int windowId = 0)
//                {
//                    return  aliasElements.Label(row + ROWS, 3, windowId, true);
//                }

//            }
//            public static class Schaltflaechen
//            {
//                public static IWebElement Inhalt_anzeigen(int windowId = 0)
//                {
//                    return aliasElements.Button(6, 1, windowId, true);
//                }
//            }
//        }
//        public static class Steplistenueberblick
//        {
//            public static class Tabelle
//            {

//                const int ROWS = 2;
//                public static IWebElement Programmname_Kommando_Ueberschrift(int FensterID = 0)
//                {
//                    return aliasElements.Label(1, 5, FensterID, true);
//                }
//                public static IWebElement Programmname_Kommando(int Reihe, int FensterID = 0)
//                {
//                    return aliasElements.Label(Reihe + ROWS, 5, FensterID, true);
//                }

//            }
//            public static class Schaltflaechen
//            {
//                public static IWebElement Spool(int FensterID = 0)
//                {
//                    return aliasElements.Button(34, 1, FensterID, true);
//                }
//            }
//        }
//        public static class Jobuebersicht
//        {
//            public static class Tabelle
//            {
//                const int REIHEN = 11;
//                public static IWebElement Jobname(int Reihe, int FensterID = 0)
//                {
//                    return aliasElements.Label(Reihe + REIHEN, 4, FensterID, true);
//                }
//                public static IWebElement Status(int Reihe, int FensterID = 0)
//                {
//                    return aliasElements.Label(Reihe + REIHEN, 56, FensterID, true);
//                }
//                public static IWebElement Datum(int Reihe, int FensterID = 0)
//                {
//                    return aliasElements.Label(Reihe + REIHEN, 84, FensterID, true);
//                }
//                public static IWebElement Uhrzeit(int Reihe, int FensterID = 0)
//                {
//                    return aliasElements.Label(Reihe + REIHEN, 95, FensterID, true);
//                }
//            }
//            public static class Schaltflaechen
//            {
//                public static IWebElement Aktualisieren(int FensterID = 0)
//                {
//                    return aliasElements.Button(8, 1, FensterID, true);
//                }
//                public static IWebElement Freigeben(int FensterID = 0)
//                {
//                    return aliasElements.Button(46, 1, FensterID, true);
//                }
//                public static IWebElement Aktive_Jobs_abbrechen(int FensterID = 0)
//                {
//                    return aliasElements.Button(25, 1, FensterID, true);
//                }
//                public static IWebElement Job_aus_Datenbank_loeschen(int FensterID = 0)
//                {
//                    return aliasElements.Button(14, 1, FensterID, true);
//                }
//                public static IWebElement Spool(int FensterID = 0)
//                {
//                    return aliasElements.Button(44, 1, FensterID, true);
//                }
//                public static IWebElement Job_Log(int FensterID = 0)
//                {
//                    return aliasElements.Button(44, 1, FensterID, true);
//                }
//                public static IWebElement Step(int FensterID = 0)
//                {
//                    return aliasElements.Button(45, 1, FensterID, true);
//                }
//                public static IWebElement Job_Details(int FensterID = 0)
//                {
//                    return aliasElements.Button(2, 1, FensterID, true);
//                }
//                public static IWebElement AppServers(int FensterID = 0)
//                {
//                    return aliasElements.Button(7, 1, FensterID, true);
//                }
//                public static IWebElement Listenstatus_anzeigen(int FensterID = 0)
//                {
//                    return aliasElements.Button(19, 1, FensterID, true);
//                }
//                public static IWebElement Layout_aendern(int FensterID = 0)
//                {
//                    return aliasElements.Button(31, 1, FensterID, true);
//                }
//                public static IWebElement Filter_setzen(int FensterID = 0)
//                {
//                    return aliasElements.Button(38, 1, FensterID, true);
//                }
//                public static IWebElement Sortieren_aufsteig(int FensterID = 0)
//                {
//                    return aliasElements.Button(41, 1, FensterID, true);
//                }
//            }
//        }
//        public static class Graphische_Anzeige
//        {
//            public static class Schaltflaechen
//            {
//                public static IWebElement Sichern_in_lokale_Datei(int FensterID = 0)
//                {
//                    return aliasElements.Button(48, 1, FensterID, true);
//                }
//            }
//            public static class Liste_sichern_in_Datei
//            {
//                public static class Schaltflaechen
//                {
//                    public static IWebElement Gruener_Haken(int FensterID = 1)
//                    {
//                        return aliasElements.Button(0, 0, FensterID, true);
//                    }
//                }
//            }
//        }
//    }
//}

