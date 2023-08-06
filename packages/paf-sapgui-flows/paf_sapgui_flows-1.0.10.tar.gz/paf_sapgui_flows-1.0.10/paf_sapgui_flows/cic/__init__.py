from paf_sapgui import window, transaction, button, field, session
from paf_sapgui.statusbar import message as statusbar_message
from paf_sapgui.session import types
from paf_sapgui_eltrans import cic as cic_elements


def open_order(order_number: str) -> bool:
    if window.get_title() != "Customer-Interaction-Center":
        transaction.open("cic0")
    else:
        cic_elements.Geschaeftspartner().alle_felder_initialisieren().click()

    cic_elements.Geschaeftspartner().suchdaten().value(order_number)
    cic_elements.Geschaeftspartner().manuelle_identifikation().click()
    if statusbar_message.get_text() == "Es konnten keine Adressen gefunden werden":
        return False
    # if (aliasGeneral.Elements.Exists(celCIC.Hitliste.Ids.Tabelle)):
    # aliasGeneral.Buttons.D Taste.Doppelklick(celCIC.Hitliste.Tabellenzelle(1, 1));
    return True


def select_order(order_number, order_type: str = None):
    search_parameter = [{"column": "VBELN", "value": order_number}]
    if order_type is not None:
        search_parameter.append({"column": "POART_EX", "value": order_type})

    row_number = cic_elements.Auftraege().MsdAuftraege().tabelle().find_row(search_parameter)
    if row_number is not None:
        cic_elements.Auftraege().MsdAuftraege().tabelle().row(row_number)
        return
    print(f"It was not possible to find the desired order {order_number} - {order_type}")


if __name__ == "__main__":
    session.session_data(user="ckoeste1", password="ne8DDP%e!vuX", system=types.SapSystems.V35)
    session.create()
    select_order("890890", 2)
