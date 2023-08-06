import random
import sys
# ZJMV_JWAKTDRER
from datetime import datetime, timedelta

from gui.sap.gui.components.actions import keys, buttons
from gui.sap.gui.components.actions import main as komponente_actions
from gui.sap.gui.components.bars import main as asit_bars
from gui.sap.gui.components.elements import transactions, sessions, windows
from gui.sap.gui.components.fields import labels
from gui.sap.gui.components.pflegeview import main as komponente_pflegeview
from gui.sap.gui.components.se16 import main as komponente_se16
from gui.sap.gui.components.tabs import main as tabs
from gui.sap.gui.element_libraries.transactions.jw25_26_27 import elements as jw27_elemente
from gui.sap.gui.element_libraries.transactions.jw34_35_36 import elements as jw36_elemente
from gui.sap.gui.element_libraries.transactions.zjkt_se import elements as zjkt_se_elemente
from tools import main as generators





def ausfuehrung():
    vorbereitungen()




# ' ###################################################




if __name__ == "__main__":
    zjkt_se.basis.werbeaktion = sys.argv[1]

    ausfuehrung()
