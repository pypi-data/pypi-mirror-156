def protokoll(Werte):
    pass
    # lstrWert = ""
    # For Each lstrWert In Werte
    # larrWerte = split(lstrWert, "-->")
    # if SapGui_Parameter.leer(larrWerte(1)) = false Then
    # lstrWert = lstrWert & "|" & larrWerte(0) & ": " & Parameter(larrWerte(1))
    # End if
    # Next

    # TODO: Sap_Prot.schreibe "ZJKT_SE", lstrWert, "OK"

class Helfer:
    @staticmethod
    def personendaten(feldertyp: zjkt_se_elemente.name_and_addresstypes):
        vorname, nachname, geschlecht, geschlecht_ansprache, geschlecht_nummer = generators.name.create_firstname_lastname(in_sap_format=True)

        zjkt_se_elemente.Auftraggeber.Basisdaten.anrede(feldertyp, geschlecht_nummer)
        zjkt_se_elemente.Auftraggeber.Basisdaten.nachname_firma_1(feldertyp, nachname)
        zjkt_se_elemente.Auftraggeber.Basisdaten.vorname_firma_2(feldertyp, vorname)

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Anrede: " & larrlName.Item("Geschlecht") & "|Vorname: " & larrlName.Item("Vorname") & "|Nachname: " & larrlName.Item("Nachname"), "OK"

    @staticmethod
    def anschrift(feldertyp: zjkt_se_elemente.name_and_addresstypes):
        strasse, hausnummer, plz, ort = generators.address.create()

        zjkt_se_elemente.Auftraggeber.Basisdaten.create_street(feldertyp, strasse)
        zjkt_se_elemente.Auftraggeber.Basisdaten.nr(feldertyp, hausnummer)
        zjkt_se_elemente.Auftraggeber.Basisdaten.plz(feldertyp, plz)
        zjkt_se_elemente.Auftraggeber.Basisdaten.ort(feldertyp, ort)

        # TODO: Postfach
        # TODO: Land

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Strasse: " & larrlAdresse.Item("Strasse") & "|Hausnummer: " & larrlAdresse.Item("Hausnummer") & "|PLZ: " & larrlAdresse.Item("Postleitzahl") & "|Ort: " & larrlAdresse.Item("Ort"), "OK"

    @staticmethod
    def selektiere_zugabe(nummer_zugabe: str, typ_zugabe: str, nummer_zugabenfeld):
        if not nummer_zugabe:
            return
        zugabenfeld = "Auftraggeber - "
        if typ_zugabe == "Ersatz":
            zugabenfeld = zugabenfeld & "Ersatzzugabe - " & str(nummer_zugabenfeld)
        else:
            zugabenfeld = zugabenfeld & "Zugabe - " & str(nummer_zugabenfeld)

        zjkt_se_elemente.Auftraggeber.Basisdaten.zugabe_1("SETFOCUS")
        keys.f4_key()

        if asit_bars.statusbar.message.get_text() != "Keine Werte gefunden":
            gefunden = False
            if windows.is_active(1) == True:
                lintZaehler = 3
                while labels.exists(column=1, row=lintZaehler, window_id=1) and not gefunden:
                    local_label = labels.create(column=29, row=lintZaehler, window_id=1)
                    if local_label._text == nummer_zugabe:
                        local_label.setFocus()
                        gefunden = True
                    else:
                        lintZaehler += 1
            keys.f2_key(1)

    @staticmethod
    def pruefung_enter():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es muss nur ENTER gedr?ckt werden", "OK"
        keys.enter_key()
        if windows.get_title() != "ASV Einstieg Schnellerfassung":
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es muss noch einmal gespeichert werden", "OK"
            buttons.speichern()