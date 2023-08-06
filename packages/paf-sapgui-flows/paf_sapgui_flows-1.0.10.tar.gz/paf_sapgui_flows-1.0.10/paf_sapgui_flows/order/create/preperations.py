if zjkt_se.basis.werbeaktion is None:
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Keine WAKT, suche eine per Zufall aus", "OK"
        Werbeaktion.zufaellige()

    # TODO: Sap_Prot.schreibe "ZJKT_SE", "Verarbeite die WAKT: " & Parameter("Einstieg__Werbeaktion"), "OK"
if zjkt_se.basis.werbeaktion is not None:
        Werbeaktion.execute_check()
        Werbeaktion.zugaben()
        Werbeaktion.hole_kid()


def zufaellige():
        werbeaktionen = ["10168999", "10150049", "10150073", "10165107", "10167546", "10163534", "10164702", "10164699",
                         "10164697", "10164701", "10164698"]
        zjkt_se.basis.werbeaktion = werbeaktionen[random.randint(1, len(werbeaktionen))]

    def pruefung():
        jw27_elemente.open_transaction(7)
        jw27_elemente.Selektion.werbeaktion(zjkt_se.basis.werbeaktion)
        keys.enter_key()

        jw27_elemente.tableiste(jw27_elemente.Tabs.faktura)
        zjkt_se.zahlart = jw27_elemente.Faktura.Zahlweg("GET")
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Habe f?r die WAKT '" & Parameter("Einstieg__Werbeaktion") & "' die folgenden Daten geholt: Zahlweg -> " & Parameter("Faktura__Zahlweg"), "OK"

    def zugaben():
        ## TODO: Sap_Prot.schreibe "ZJKT_SE", "Schaue bei der WAKT '" & Parameter("Einstieg__Werbeaktion") & "' nach den Zugaben", "OK"
        jw36_elemente.open_transaction(6)

        jw36_elemente.Selektion.Verkaufsorganisation("")
        jw36_elemente.Selektion.Vertriebsweg("")
        jw36_elemente.Selektion.Sparte("")
        jw36_elemente.Selektion.Werbeart("")
        jw36_elemente.Selektion.Beginn_Werbebasis("")
        jw36_elemente.Selektion.Werbeaktion(zjkt_se.basis.werbeaktion)
        keys.f4_key()
        buttons.green_tick(1)

        labels.set_focus(1, 3, 1)
        buttons.green_tick(1)

        if tabs.exists_tab(jw36_elemente.Tabs.sachpraemien):
            jw36_elemente.Sachpraemien.set_tab()
            zjkt_se.zugaben = jw36_elemente.Sachpraemien.get_zugaben()

            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die WAKT hat die folgenden Zugaben: " & Parameter("Zugaben"), "OK"
        else:
            pass
            # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die WAKT hat keine Zugaben", "OK"

    def hole_kid():

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Schaue nach der passenden KID", "OK"
        transactions.set("zjkta_kidwakt")
        komponente_pflegeview.select_by_contents([{"Werbeaktion": zjkt_se.basis.werbeaktion}])

        zjkt_se.kid = sessions.sessions.findById("wnd[0]/usr/tblSAPLZJCFU_KIDWAKTTCTRL_ZJKV_KIDWAKT/ctxtZJKV_KIDWAKT-KID[1,0]")

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Die KID f?r die WAKT '" & Parameter("Einstieg__Werbeaktion") & "' ist: " & Parameter("Einstieg__KID"), "OK"

    def hole_iban():
        # TODO: Sap_Prot.schreibe "ZJKT_SE", "Es wird eine IBAN gebraucht, suche eine per Zufall", "OK"
        komponente_se16.open_table("TIBAN")
        komponente_se16.selection_screen.fields_for_selection(["BANKS", "VALID_FROM"])
        komponente_se16.selection_screen.create_selection_field(position=1, value="DE")
        komponente_se16.selection_screen.create_selection_field(position=2, value=datetime.today() - timedelta(months=8))

        komponente_actions.key.f8_key()

        local_table = komponente_se16.table.create()
        max_random_value = 20

        if local_table.rowCount < 20:
            max_random_value = local_table.rowCount

        zjkt_se.iban = local_table.getCellData(random.randint(1, max_random_value), "#6")

        # TODO: Sap_Prot.schreibe "ZJKT_SE", "IBAN: " & Parameter("Auftraggeber__IBAN"), "OK"

