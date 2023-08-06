from paf_sapgui_component_actions import key, button
from paf_sapgui_component_elements import window
from paf_sapgui_component_bars.statusbar import message

import window_0
import window_1


def execute():
    # TODO: Sap_Prot.schreibe "ZJKT_SE", "?berpr?fe auf Meldungen", "OK"
    key.enter_key()

    if window.is_active():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Auftrag wird noch gespeichert", "OK"
        button.save()

    max_rounds = 20

    for lintSicherheitszaehler in max_rounds:
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Durchlauf " & lintSicherheitszaehler, "OK"
        if window.is_active(1):

            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Ein weiteres Fenster ist aktiv, ?berpr?fe es", "OK"
            lstrRueckmeldung = window_1.execute_check(window.get_title(1))
        elif window.is_active(2):
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es sind zwei Fenster aktiv, ?berp?fe das oberste", "OK"
            lstrRueckmeldung = window_1.execute_check(window.get_title(1))
        else:
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Keine Fenster aktiv, pr?fe auf Meldungen", "OK"
            if message.get_text() == "":
                button.save()

            lstrRueckmeldung = window_0.pruefung(window.get_title())

        if lstrRueckmeldung == "Ende":
            pass
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Der Auftrag wurde erfolgreich mit der VBELN " & Parameter("AUS_Auftragsnummer") & " gespeichert", "OK"
