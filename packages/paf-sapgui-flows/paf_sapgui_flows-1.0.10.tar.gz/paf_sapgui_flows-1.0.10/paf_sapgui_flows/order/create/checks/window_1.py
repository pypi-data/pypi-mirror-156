from datetime import datetime
from paf_sapgui_component_elements import window

from paf_sapgui_component_actions import key

def execute_check(window_title: str):
    if "Opt-In Erfassung" in window_title: 
        opt_in()
    if "Auswahl-Liste m?glicher Stra?en" in window_title: 
        moegliche_strassen()
    if "Auswahl lieferbare Planvertriebsausgaben" in window_title: 
        vertriebsausgaben()
    if "sicht Provisionsempf?nger" in window_title: 
        provisionsempfaenger()
    if "uswahl Zahlar" in window_title: 
        auwahl_zahlart()
    if "Information" in window_title: 
        verschiedenes()


def opt_in():
    if window.is_active(1):
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Setze Opt-In mit heutigem Datum", "OK"
        zjkt_se_elemente.opt_in_dialog.einholdatum(datetime.now().strftime("%d.%m.%Y"))
        key.f8_key(1)
        # TODO: Druckdialog


def moegliche_strassen():
    # TODO: Sap_Prot.schreibe "ZJKT_SE", "Stra?e war nicht ganz klar, setze eine.", "OK"
    labels.set_focus(2, 5, 1)
    buttons.green_tick(1)


def vertriebsausgaben():
    while windows.is_active(1):
        labels.set_focus(1, 4, 0)
        buttons.green_tick(1)


def provisionsempfaenger():
    # TODO: Sap_Prot.schreibe "ZJKT_SE", "W?hle Provisionsempf?nger", "OK"
    labels.set_focus(1, 4, 0)
    buttons.green_tick(1)


def auswahl_zahlart():
    # TODO: Sap_Prot.schreibe "ZJKT_SE", "Auswahl der Zahlart", "OK"
    if zjkt_se.faktura.zahlart == "Verrechnung":
        pass
        # TODO: SAPGuiSession("S").SAPGuiWindow("F1").SAPGuiButton("containername:=usr", "guicomponenttype:=40", "name:=SPOP-VAROPTION1", "type:=GuiButton").Click
    if zjkt_se.faktura.zahlart == "Orderscheck":
        pass
        # TODO: SAPGuiSession("S").SAPGuiWindow("F1").SAPGuiButton("containername:=usr", "guicomponenttype:=40","name:=SPOP-VAROPTION2", "type:=GuiButton").Click


def verschiedenes():
    # TODO: lstrFensterInhalt = SapGui_Fenster.Inhalt(lintFenster)
    fensterinhalt = ""
    # Archivierungsproblem

    if "Archivierungsproblem" in fensterinhalt:
        fensternummer = 2 if windows.is_active(2) else 1
        buttons.green_tick(fensternummer)
        # Logge den Fehler
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Archivierungsproblem, schlie?e Fenster", "OK"
