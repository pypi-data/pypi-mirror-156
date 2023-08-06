import

def main():
    preperations()
    if zjkt_se.faktura.zahlart is not None:
        Werbeaktion.hole_iban()
    Eingabemasken.einstieg()
    # Eingabemasken.Eingaben_PVA()
    Eingabemasken.person()
    Eingabemasken.zugaben()
    Eingabemasken.zahlungsmodalitaeten()
    Eingabemasken.faktura()
    Eingabemasken.auftrag()
    Eingabemasken.zusaetzliche_daten()
    Pruefung.Ablauf()

if __name__ == "__main__":
    main()