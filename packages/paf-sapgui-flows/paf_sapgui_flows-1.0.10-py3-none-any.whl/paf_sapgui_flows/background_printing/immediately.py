from gui.sap.gui.components.actions import keys
from gui.sap.gui.element_libraries.misc.background_print import elements


def execute():
    elements.start_background_printing(0)
    keys.f6_key(1)
    elements.Startterminwerte.Sofort(True)
    keys.enter_key(1)
    elements.Startterminwerte.Sichern(True)
