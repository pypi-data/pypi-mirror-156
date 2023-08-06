//namespace AS.Auto.Web.Sap.Gui.Elemente.Vx.Programme
//{
//  using OpenQA.Selenium;
//  using aliasElements = As.It.Ses.Frameworks.Selenium.Sap.Gui.Selection.Elements;
//  using aliasButtons = As.It.Ses.Frameworks.Selenium.Sap.Gui.Selection.Buttons;

//  public static class Zjvr_Rjvnetch
//  {
//    // Schaltflächen
//    public static class Schaltflaechen { }
//    public static class Felder
//    {
//      public static IWebElement Auftragsnummer_von()
//      {
//        return aliasElements.CreateElement("M0:46:::1:34");
//      }
//      public static IWebElement Auftragsnummer_bis()
//      {
//        return aliasElements.CreateElement("M0:46:::1:59");
//      }
//      public static IWebElement Testlauf()
//      {
//        return aliasElements.CreateElement("M0:46:::2:0-txt");
//      }
//    }
//    public static class Ablaeufe
//    {
//      public static bool Fehler_beheben(string VBELN)
//      {
//        Felder.Auftragsnummer_von().Clear();
//        Felder.Auftragsnummer_bis().Clear();

//        Felder.Auftragsnummer_von().SendKeys(VBELN);
//        Felder.Auftragsnummer_bis().SendKeys(VBELN);

//        Felder.Testlauf().Click();
//        aliasButtons.Execute();

//        if (aliasElements.Exists("M0:46:::0:0_l"))
//        {
//          return true;
//        }
//        return false;
//      }
//    }

//  }
//}
