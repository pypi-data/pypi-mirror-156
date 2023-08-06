
																					 
Parameter("AUS_Abstimmschluessel") = ""

If SapGui_Tabellen.wird_angezeigt = true Then
	SapGui_Tabellen.feldbezeichner
	
	For lintReihenzaehler = 1 To SapGui_Tabellen.Objekt.RowCount Step 1
		Parameter("AUS_Abstimmschluessel") = Parameter("AUS_Abstimmschluessel") & SapGui_Tabellen.Objekt.GetCellData (lintReihenzaehler,"Abstimmschlüssel") & ","
	Next
End If		

Parameter("AUS_Abstimmschluessel") = mid(Parameter("AUS_Abstimmschluessel"),1,len(Parameter("AUS_Abstimmschluessel"))-1)