    def pruefung(window_title):
        lstrFunction = ""
        lboolAllePruefungen = False

        if window_title == "Dublettentrefferliste":
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es wurde eine Dublette gefunden, breche ab", "OK"
            buttons.back()
        if window_title == "ASV Einstieg Schnellerfassung":
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die Einstiegsmaske wird angezeigt", "OK"
            Pruefung_Fenster_0 = Pruefung.Fenster_0.erfolgreich_angelegt()  # Fertig, lese Werte in Parameter

        lboolAllePruefungen = True

        if lboolAllePruefungen:
            status_bar_text = asit_bars.statusbar.message.get_text()
            if "Die Postleitzahl pa?t nicht zur Stra?e" in status_bar_text: Pruefung.Fenster_0.plz_falsch()
            if "die Auftragsart EHFT ist ein Starttermin zwingen" in status_bar_text: Pruefung.Fenster_0.ehft()
            if ".*itte geben Sie den Lieferende Grund a." in status_bar_text: Pruefung.Fenster_0.lieferende_grund()
            if "Pr?mienart .* darf nicht nach Land  versendet werden. Bitte pr?fen" in status_bar_text: Pruefung.Fenster_0.zugabe()
            if "ist eine Pr?mie obligatorisch" in status_bar_text: Pruefung.Fenster_0.zugabe()
            if "Die Postleitzahl pa?t nicht zur Strasse" in status_bar_text: Pruefung.Fenster_0.adresse_falsch()
            if "Sie alle Mu?felder" in status_bar_text: Pruefung.Fenster_0.pflichtfelder()
            if "in Rolle 'Vertriebskunde' nicht vorhanden" in status_bar_text: Helfer.pruefung_enter()
            if "Der r?ckw. Positionsbeginn mu? vor dem " in status_bar_text: Helfer.pruefung_enter()
            if "UNISERV Dublettencheck ist nicht aktiv" in status_bar_text: Helfer.pruefung_enter()
            if "Zahlweg E erfordert g?ltige Bankverbindung" in status_bar_text: Pruefung.Fenster_0.iban()
            if "Angabe eines Vermittlers ist obligatorisch" in status_bar_text: Pruefung.Fenster_0.vermittler_obligatorisch()
            if "Auftragsdublette" in status_bar_text: Helfer.pruefung_enter()
            if "Zahler-Bezieher-Konstellation darf WE und AG nicht ?bereinstimmen" in status_bar_text: Pruefung.Fenster_0.abweichender_we()
            if "ein Nummernkreis f?r SEPA-Mandate vorhande" in status_bar_text: Helfer.pruefung_enter()
            if "Verb. erfolgr. Auftr." in status_bar_text: Pruefung.Fenster_0.erfolgreich_angelegt()
            if "ugabe" in status_bar_text and "ung?lti" in status_bar_text: Pruefung.Fenster_0.zugabe_ungueltig()
            if "ank-ID f?r Gesch?ftspartner.*konnte nicht ermittelt werde" in status_bar_text: Helfer.pruefung_enter()
            if "eschenkabo braucht abweichenden Warenempf?nge" in status_bar_text: Pruefung.Fenster_0.abweichender_we()

    def zugabe_ungueltig():
        # TODO: Zugabe ung?ltig
        """
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die Zugabe ist ung?ltig", "OK"
        lintFalscheZugabeNummer = cint(SapGui_Statusleiste.Wert(1))
        key.enter_key()

        SapGui_Elemente.CEF("ZJKS_AI_ORDER-ZUGABE1", 0).Set cstr(lintFalscheZugabeNummer + 1)
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Neue Zugabe: " + cstr(lintFalscheZugabeNummer + 1), "OK"
        key.enter_key()

        Helfer.pruefung_enter()
        """

    def plz_falsch():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die PLZ ist falsch, setze eine neue Adresse", "OK"
        keys.enter_key()
        Helfer.anschrift()
        keys.enter_key()

        Helfer.pruefung_enter()

    def ehft():
        # TODO: Einzelheft
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Einzelheft", "OK"
        """
        key.enter_key()
        opt_in()

        lstrYear = ""
        lstrWeek = ""

        Select Case SapGui_Elemente.CEF("JDTDRER-BEZEI10", 0).GetROProperty("value")
            Case "AUTO BILD":
                # Autobild erscheint immer am Donnerstag
                lintWeek = DatePart("ww", date, vbMonday, vbFirstFourDays)
                lintYear = Year(date)
                lintWeek = lintWeek - 2
                if lintWeek <= 0 Then
                    lintWeek = 52
                    lintYear = lintYear - 1
                End if

                lstrYear = cstr(lintYear)
                lstrWeek = cstr(lintWeek)

                Select Case len(lstrWeek)
                Case 3:
                    lstrWeek = "0" & lstrWeek
                Case 2:
                    lstrWeek = "00" & lstrWeek
                Case 1:
                    lstrWeek = "000" & lstrWeek
                End Select
        End Select

        SapGui_Elemente.CEF("ZJKS_AI_ORDER-TERMVON", 0).Set
        lstrWeek & "/" & lstrYear
        SapGui_Elemente.CEF("ZJKS_AI_ORDER-TERMBIS", 0).Set
        lstrWeek & "/" & lstrYear

        SapGui_Taste.Entertaste 0

        Helfer.pruefung_enter()
        End if
        """

    def lieferende_grund():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Lieferendegrund fehlt, setze 109", "OK"
        keys.enter_key()

        Pruefung.Fenster_1.opt_in()

        zjkt_se_elemente.Auftrag.lf_ende_grd("109")

        keys.enter_key()

        Helfer.pruefung_enter()

    def zugabe():
        pass
        # D?rfte nicht mehr ben?tigt werden, da am Anfang eine IBAN gesucht wird
        # SAPGuiSession("S").SAPGuiWindow("F").SendKey ENTER
        # OptIn
        # Auftraggeber_Zugabe

    def pflichtfelder():
        # TODO: Mitarbeiter-Abo
        """
        if SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Kostenstelle").GetROProperty("required") = True Then
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die Kostenstelle musste gesetzt werden, habe die 10 genommen", "OK"
            SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Kostenstelle").Set "10"

        Helfer.pruefung_enter()
        """

    def iban():
        pass
        # D?rfte nicht mehr ben?tigt werden, da am Anfang eine IBAN gesucht wird
        # SAPGuiSession("S").SAPGuiWindow("F").SendKey ENTER
        # SAPGuiSession("S").Parameter_Leer "Auftraggeber__IBAN", "DE12500105170648489890"
        # SAPGuiSession("S").SAPGuiWindow("Schnellerfassung").SAPGuiEdit("Auftraggeber - IBAN") = Parameter("Auftraggeber__IBAN")
        # SAPGuiSession("S").SAPGuiWindow("F").SendKey ENTER

    def vermittler_obligatorisch():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es wird ein Vermittler ben?tigt", "OK"
        zjkt_se_elemente.Vermittler.select_tab()

        keys.enter_key()
        Helfer.personendaten()
        Helfer.anschrift()

        keys.enter_key()
        zjkt_se_elemente.Auftraggeber.select_tab()

        Helfer.pruefung_enter()

    def abweichender_we():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es wird ein abweichender Warenempf?nger ben?tigt", "OK"
        keys.enter_key()

        Pruefung.Fenster_1.opt_in()

        zjkt_se_elemente.Warenempfaenger.select_tab()
        keys.enter_key()

        Helfer.personendaten()
        Helfer.anschrift()

        keys.enter_key()
        zjkt_se_elemente.Auftraggeber.select_tab()

        if windows.get_title(0) == "Dublettentrefferliste":
            keys.f12_key()

        Helfer.pruefung_enter()

    def dubletten():
        keys.f12_key()

    def erfolgreich_angelegt():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Alle Pr?fungen erfolgreich", "OK"
        return "Ende", asit_bars.statusbar.message.get_text()
