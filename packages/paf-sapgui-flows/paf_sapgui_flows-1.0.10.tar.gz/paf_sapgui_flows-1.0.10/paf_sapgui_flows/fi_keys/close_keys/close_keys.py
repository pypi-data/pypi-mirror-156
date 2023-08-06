from datetime import datetime, timedelta

from gui.sap.gui.components.actions import keys
from gui.sap.gui.components.se16 import main as asit_se16
from gui.sap.gui.components.se16 import main, tables
from gui.sap.gui.components.se16 import selection_screen

fi_keys = None


def execute():
    if fi_keys is not None:
        __close_fi_keys(__check_fi_keys())
    else:
        __close_fi_keys(__get_open_fi_keys())


def set_fi_keys(*fi_keys_to_set):
    fi_keys = []
    fi_keys.extend(fi_keys_to_set)


def __get_open_fi_keys():
    # Werkzeuge_Protokollierung.schreibe "RFKKFIKEYCLOSE", "Hole offene Abstimmschl�ssel", "OK"
    asit_se16.open_table("DFKKSUMC")

    # '1 = FIKEY = Abstimmschl�ssel
    # '2 = FIKST = Status
    # '3 = CPUDT = Erfassungsdatum
    # '4 = XUEVO = �bernahme komplett

    selection_screen.fields_for_selection(['FIKEY', 'FIKST', 'CPUDT', 'XUEVO'])
    selection_screen.field_value('SD*', 1)
    selection_screen.field_value('', 2)
    selection_screen.set_selection_option_with_value((datetime.today() - timedelta(days=1)).strftime('%d.%m.%Y'), 3,
                                                     selection_type='gog')
    selection_screen.set_selection_option_with_value("X", 4, selection_type='ungleich')

    keys.f8_key()

    if tables.is_displayed():
        return tables.get_values_from_column("FIKEY")


def __close_fi_keys(open_fi_keys):
    pass
    # paf_sapgui_elprog.open_table('RFKKFIKEYCLOSE')
    # Werkzeuge_Protokollierung.schreibe "RFKKFIKEYCLOSE", "Schlie�e offene Abstimmschl�ssel", "OK"
    # if type(open_fi_keys) == "list":
    # if len(open_fi_keys.Count) > 0:


# SapGui_Programme.Oeffne "RFKKFIKEYCLOSE",""

# SapGui_Selektion.Einzelwerte_selektieren open_fi_keys
# SapGui_Selektion.Mehrfachselektion "R_FIKEY"
# SapGui_Taste.F8_Taste 0


# TODO: Pr�fung

def __check_fi_keys():
    local_fi_keys = []
    if ',' in local_fi_keys:
        split_up_fi_keys = local_fi_keys.split(',')
        for fi_key in split_up_fi_keys:
            local_fi_keys.append(fi_key)
        fi_key_count = len(local_fi_keys)
    else:
        fi_key_count = 1
        local_fi_keys.append(local_fi_keys)

    return local_fi_keys
