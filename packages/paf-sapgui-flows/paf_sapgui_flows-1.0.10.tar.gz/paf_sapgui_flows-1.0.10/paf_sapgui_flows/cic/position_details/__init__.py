from paf_sapgui_eltrans import cic as cic_elements
from ... import cic as cic_flow
from paf_sapgui.statusbar import message


def change_text(order_number: str, the_text: str, overwrite: bool = False) -> tuple[bool, str | None]:
    order_displayed = cic_flow.open_order(order_number)
    if not order_displayed:
        return False, message.get_text()
    cic_flow.select_order(order_number)
    cic_elements.Auftraege().MsdAuftraege().details_zur_position_anzeigen().click()
    cic_elements.Auftraege().DetailsZurPosition().Tabs().text().select()
    cic_elements.Auftraege().DetailsZurPosition().Text().anzeigen_aendern().click()

    if not overwrite:
        existing_text = cic_elements.Auftraege().DetailsZurPosition().Text().text_element().value()
        new_text = the_text + "\n" + existing_text
        cic_elements.Auftraege().DetailsZurPosition().Text().text_element().value(new_text)
    else:
        cic_elements.Auftraege().DetailsZurPosition().Text().text_element().value(the_text)
    cic_elements.Auftraege().DetailsZurPosition().Text().sichern().click()

    return True, None
