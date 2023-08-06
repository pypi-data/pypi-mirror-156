    def einstieg():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Starte die Anlage eines Auftrags in der Transaktion 'ZJKT_SE'", "OK"
        if zjkt_se.basis.werbeaktion == "":
            print("Fehler, keine WAKT vorhanden")
            quit()

        zjkt_se_elemente.open_transaction()
        zjkt_se_elemente.Selektion.werbeaktion(value=zjkt_se.basis.werbeaktion)
        if zjkt_se.kid is not None:
            zjkt_se_elemente.Selektion.kampagnen_id(value=zjkt_se.kid)
        # SapGui_Elemente.CEF("JKAP-ZZ_KEZI_SPLIT", 0).Set Parameter("Einstieg__Splitkennzeichen")

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "WAKT: " & Parameter("Einstieg__Werbeaktion") & "|KID: " & Parameter("Einstieg__KID") & "| Splitkennzeichen: " & Parameter("Auftrag__Splitkennzeichen"), "OK"

        keys.enter_key()

        if windows.is_active(1):
            labels.set_focus(1, 4, 1)
            buttons.green_tick(1)

    def pva():
        pass
        # if SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Allgemein__PVA").GetROProperty("required") = True And SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Allgemein__PVA").GetROProperty("enabled") = True Then
        # SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Allgemein__PVA").SetFocus
        # SAPGuiSession("S").SAPGuiWindow("F").SendKey F4

        # SAPGuiSession("S").SAPGuiWindow("F1").SAPGuiButton("containername:=tbar\[0\]", "guicomponenttype:=40", "name:=btn\[0\]","type:=GuiButton").Click
        # SAPGuiSession("S").SAPGuiWindow("F1").SAPGuiLabel("guicomponenttype:=30", "relativeid:=wnd\[1\]/usr/lbl\[1,3\]","type:=GuiLabel").SetFocus
        # SAPGuiSession("S").SAPGuiWindow("F1").SAPGuiButton("containername:=tbar\[0\]", "guicomponenttype:=40", "name:=btn\[0\]","type:=GuiButton").Click
        # End if

    # def Helfer_ParameterFeld(Parametername, Wert, Feldname):
        # if Parameter(Parametername) = "" Then
            # SapGui_Elemente.CEF(Feldname, 0).Set Wert
        # Else
            # SapGui_Elemente.CEF(Feldname, 0).Set Parameter(Parametername)

    def person():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "F?lle die Daten zur Person ein", "OK"
        zjkt_se.positionsart = zjkt_se_elemente.Basis.positionsart(value="GET")

        if zjkt_se.geschaeftspartner is not None:
            zjkt_se_elemente.Auftraggeber.Basisdaten.geschaeftspartner(value=zjkt_se.geschaeftspartner)
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "GP-Nr.: " & Parameter("Auftraggeber__Geschaeftspartner"), "OK"
        else:
            Helfer.personendaten(zjkt_se_elemente.name_and_addresstypes.auftraggeber)
            Helfer.anschrift(zjkt_se_elemente.name_and_addresstypes.auftraggeber)
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Strasse: " & larrlAdresse.Item("Strasse") & "|Hausnummer: " & larrlAdresse.Item("Hausnummer") & "|PLZ: " & larrlAdresse.Item("Postleitzahl") & "|Ort: " & larrlAdresse.Item("Ort"), "OK"

    def zugaben():
        if zjkt_se.zugaben is not None:
            # lstrZugabe = Parameter("Zugaben")
            if "," in zjkt_se.zugaben:
                zjkt_se.zugaben = zjkt_se.zugaben.split(",")
                # lstrZugabe = "00" & cstr(RandomNumber(0, Ubound(larrZugaben) - 1) + 1)
            else:
                zjkt_se.zugaben = "001"

            zjkt_se_elemente.Auftraggeber.Basisdaten.zugabe_1(zjkt_se.zugaben)
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Zugabe: " & lstrZugabe, "OK"

    def zahlungsmodalitaeten():

        # SapGui_Elemente.CEF("ZJGS_AI_BP-BANKS", 0).Set Parameter("Auftraggeber__Bankland")
        # SapGui_Elemente.CEF("ZJGS_AI_BP-CCINS", 0).Set Parameter("Auftraggeber__Kartenart")

        if zjkt_se.iban is not None:
            zjkt_se_elemente.Auftraggeber.Basisdaten.iban(zjkt_se.iban)

        # SapGui_Elemente.EF("ZJGS_AI_BP-CCNUM", 0).Set Parameter("Auftraggeber__Kartennummer_CCV")
        # SapGui_Elemente.EF("ZJGS_AI_BP-ZZBIC", 0).Set Parameter("Auftraggeber__BIC")
        # SapGui_Elemente.EF("ZJGS_AI_BP-BANKN", 0).Set Parameter("Auftraggeber__Bankkonto")
        # SapGui_Elemente.EF("ZJGS_AI_BP-ZZ_CCDAT", 0).Set Parameter("Auftraggeber__Gueltig_bis")
        # SapGui_Elemente.EF("ZJGS_AI_BP-BANKL", 0).Set Parameter("Auftraggeber__Bankschluessel")

        # larrWerte = array(_
        # "Bankland-->Auftraggeber__Bankland", _
        # "Kartenart-->Auftraggeber__Kartenart", _
        # "IBAN-->Auftraggeber__IBAN", _
        # "Kartennummer_CCV-->Auftraggeber__Kartennummer_CCV", _
        # "BIC-->Auftraggeber__BIC", _
        # "Bankkonto-->Auftraggeber__Bankkonto", _
        # "G?ltig_bis-->Auftraggeber__Gueltig_bis", _
        # "Bankschl?ssel-->Auftraggeber__Bankschluessel")

        # Protokoll larrWerte



    def faktura():
        # SapGui_Parameter.Befuelle_Feld "Faktura__Fakturaperiodizitaet", "ZJKS_AI_ORDER-FKPER.", Null, true, 0
        if zjkt_se.faktura.zahlart is not None:
            zjkt_se_elemente.Auftraggeber.faktura.zahlweg(zjkt_se.faktura.zahlart)
        # SapGui_Parameter.Befuelle_Feld "Faktura__Zahlweg", "ZJKS_AI_ORDER-ZLSCH", Null, true, 0

        # larrWerte = array(_
        # "Fakturaperiodizit?t-->Faktura__Fakturaperiodizitaet", _
        # "Fakturatermin-->Faktura__Termin", _
        # "Zahlweg-->Faktura__Zahlweg")

        # Protokoll larrWerte

        if zjkt_se_elemente.Auftraggeber.faktura.zahlweg("GET") == "":
            zjkt_se_elemente.Auftraggeber.faktura.zahlweg("R")

    def auftrag():
        if zjkt_se.bestellart is not None:
            zjkt_se_elemente.Auftraggeber.auftrag.bestellart(zjkt_se.bestellart)

        # SapGui_Parameter.Befuelle_Feld "Auftrag__Adressquelle", "ZJKS_AI_ORDER-ADR_QUELLE", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Auftrag__Menge", "ZJKS_AI_ORDER-ETMENGE", Null, true, 0
        if zjkt_se.bestelldatum is not None:
            zjkt_se_elemente.Auftraggeber.auftrag.bestelldat(zjkt_se.bestelldatum)
        else:
            zjkt_se_elemente.Auftraggeber.auftrag.bestelldat(datetime.now().strftime("%d.%m.%Y"))
        # SapGui_Parameter.Befuelle_Feld "Auftrag__Splitkennzeichen", "JKAP-ZZ_KEZI_SPLIT", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Auftrag__Werbender_ASH", "ZJKS_AI_ETB-ASH", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Auftrag__Agenturwerber", "ZJKS_AI_ORDER-ZZ_AGBWERB", Null, true, 0

        # larrWerte = array(_
        # "Bestellart-->Auftrag__Bestellart", _
        # "Adressquelle-->Auftrag__Adressquelle", _
        # "Bestelldatum-->Auftrag__Bestelldatum", _
        # "Splitkennzeichen-->Auftrag__Splitkennzeichen", _
        # "Werbender ASH-->Auftrag__Werbender_ASH", _
        # "Agenturwerber-->Auftrag__Agenturwerber", _
        # "Menge-->Auftrag__Menge")

        # Protokoll larrWerte

    def zusaetzliche_daten():
        pass
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Bezugsperiodizitaet", "ZJKS_AI_ORDER-BEZPER", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Vertragskonto", "ZJKS_AI_ORDER-VKONT", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Druck_WE", "ZJKS_AI_ORDER-ZZ_KZDRUCK", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Anzahl", "ZJKS_AI_ORDER-ZZ_ANZAHL", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Medium", "ZJKS_AI_ORDER-ZZ_MEDIUM", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Referenzbeleg", "ZJKS_AI_ORDER-ZZ_REFBELEG", Null, true, 0
        # SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Druck", "ZJKS_AI_ORDER-ZZ_KZDRUCK", Null, true, 0
        # 'SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Lieferhinweis", "ZJKS_AI_ORDER-ZZ_REFBELEG", null FELD FEHLT NOCH
        # 'SapGui_Parameter.Befuelle_Feld "Zusaetzliche_Daten__Lieferart", "ZJKS_AI_ORDER-ZZ_REFBELEG", null FELD FEHLT NOCH

        # larrWerte = array(_
            # "Bezugsperiodizit?t-->Zusaetzliche_Daten__Bezugsperiodizitaet", _
            # "Vertragskonto-->Zusaetzliche_Daten__Vertragskonto", _
            # "Druck WE-->Zusaetzliche_Daten__Druck_WE", _
            # "Anzahl-->Zusaetzliche_Daten__Anzahl", _
            # "Medium-->Zusaetzliche_Daten__Medium", _
            # "Referenzbeleg-->Zusaetzliche_Daten__Referenzbeleg", _
            # "Druck-->Zusaetzliche_Daten__Druck")

        # Protokoll larrWerte