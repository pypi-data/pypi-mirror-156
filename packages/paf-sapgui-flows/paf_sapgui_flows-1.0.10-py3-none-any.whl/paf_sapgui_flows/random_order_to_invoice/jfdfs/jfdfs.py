
class Jfdfs:
	@staticmethod
	def execute():
		# Felder:
		# 		1 = Fakt./Abr.Datum = FKDAT
		#		2 = Vertriebsweg = VTWEG
		#		3 = Fakturaart = FKART
		#		4 = Auftragsnummer = VBELN
		#		5 = Druckerzeugnis = DRERZ

		SapGui_Tabellen.oeffne "JFDFS"
		SapGui_Selektion.fields_for_selection Array("FKDAT", "VTWEG", "FKART", "VBELN", "DRERZ") # W�hle die Felder aus, welche Werte in der Selektion enthalten k�nnen

		SapGui_Selektion.create_selection_field(2, "von", true, 0).Set Parameter("Vertriebsweg") # Feld "Vertriebsweg"

		If Parameter("Fakturadatum") = "01.01.1900" OR Parameter("Fakturadatum") = "" then
	
			Parameter("Fakturadatum") = "01." & holeMonatJahr
			SapGui_Selektion.Selektionsoption  1, "von", Parameter("Fakturadatum"), "gog",true, 0
		Else
			SapGui_Selektion.Selektionsoption 1, "von", Parameter("Fakturadatum"), "gog",true, 0
		End If
		If Parameter("Auftragsnummer") <> "" Then
			SapGui_Selektion.create_selection_field(4, "von", true, 0).Set Parameter("Auftragsnummer") # Feld "Auftragsnummer"
		else
			lstrWert = "1*"
			Select Case Parameter("Druckerzeugnis")
				Case "53","967","974","977","1138":
				lstrWert = "6*"
			End Select
		SapGui_Selektion.Selektionsoption 4, "von", lstrWert, "muster",true, 0
	End If
	If Parameter("Druckerzeugnis") <> "" Then
		SapGui_Selektion.create_selection_field(5, "von", true, 0).Set Parameter("Druckerzeugnis") # Feld "Druckerzeugnis"
	End If
	If Parameter("Fakturaart") <> "" Then
		SapGui_Selektion.create_selection_field(3, "von", true, 0).Set Parameter("Fakturaart")
	End If

	SapGui_Taste.F8_Taste 0

	If SapGui_Tabellen.wird_angezeigt = true Then
		If  SapGui_Statusleiste._text  = "Zum angegebenen Schl�ssel wurden keine Tabelleneintr�ge gefunden" Then
			Reporter.ReportHtmlEvent micFail, "Keine Fakturen", "Es konnte keine Fakturen mit den Kriterien <br />Fakturadatum: " & Parameter("Fakturadatum") & "<br />Vertriebsweg: " & Parameter("Vertriebsweg") & "<br />Druckerzeugnis: " & Parameter("Druckerzeugnis") & "<br />gefunden werden"
			exittest
		End If
	End If

	Function holeMonatJahr()
		lintMonat = Month(Date)
		If lintMonat > 6 Then
			holeMonatJahr = lintMonat - 6 & "." & Year(date)
		else
			lintJahr = Year(date) - 1
			lintMonat = 12 - (6 - lintMonat)
			holeMonatJahr = lintMonat & "." & lintJahr
		End If
	End Function
