import numpy as np
import pandas as pd
import re
import math
from datetime import datetime

data= pd.read_csv("../Data/thalia_stage2.csv")
WECHSELKURS_CHF=0.9889 #  EUR zum CHF. Stand 08.12.2022


    # Finde Int in Text. Wenn Text: Finde int. Wenn int: int , nan : nan
def find_int(txt):

    if isinstance(txt,str):
        return (re.findall(r'[0-9]+',str(txt))[0])
    elif isinstance(txt,int):
       return txt
    elif math.isnan(txt):
        return math.nan
# Finde Nummer in Auflage.
def auflage(txt):
    if isinstance(txt,str):
        return (re.findall(r'[0-9]+',str(txt))[0])+". Auflage"
    elif isinstance(txt,int):
       return str(txt)+". Auflage"
    elif math.isnan(txt):
        return math.nan
# Finde Preis
def preise(txt):
    if isinstance(txt,str):
        return float(".".join(re.findall(r'[\d\.\d]+',str(txt))))      ####https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string
    elif isinstance(txt,float):
        return txt
    elif math.isnan(txt):
        return math.nan
#Die erste Buchstabe soll grossgeschrieben werden
def capitalize_first_letter(txt):
    return str(txt[0]).replace("'","").capitalize()+str(txt[1:]).replace("'","")

# Die Striche in ISBN Nummer sollen gelöscht werden. ISBN wird zum EAN.
def isbn(txt):
      return str(txt).replace("-", "")
#Bereinige Datum
def datum(datum):
        try:
            # versuche Striche zu ersetzem und als datetime mit . zu schreiben
           return datetime.strptime(str(datum).replace("-","."),"%d.%m.%Y")
        except:
            # Wenn nicht möglich ist das Datum als z.b April 2020 gespeichert.
            jahr=str(find_int(datum))      # suche Int in dem string - das ist das Jahr
            monat=re.findall(r'[\w]+',str(datum))[0]  # finde "wörter" im Datumstring - erstes element monat
            tag="01"
            monat_dict={"Januar":"01","Februar":"02", "März":"03","April":"04","Mai":"05", "Juni":"06", \
               "Juli": "07" , "August": "08", "September":"09", "Oktober":"10", \
               "November":"11", "Dezember":"12"}
            monat_nr=monat_dict[monat]  # finde Monatnummer aufgrund von der Dictionary  mit dem Monatname
            datum_new=tag+"."+monat_nr+"."+jahr  #String , dass das datum representiert
            return datetime.strptime(datum_new, "%d.%m.%Y")  #return von datetime

# Check ob die Information vorhanden ist oder nicht
def ist(txt):
    if  not isinstance(txt,str):
        return "Nein"
    else:
        return "Ja"

# Wenn es mehrere Namen in dem String gibt, die nicht in einer Zeile geschrieben sind,
# sollen sie eins neben anderer mit Kommas gespeichert werden
def namen(txt):
    if isinstance(txt,str):
        list_namen=str(txt).split(",")
        return '"'+", ".join([x.rstrip('\r\n').lstrip('\r\n').strip() for x in list_namen])+'"'


# Extrahiere Länge von Masse
def masse_l(txt):
    masse=str(txt).replace("cm","").replace(",",".").split("/")
    if len(masse)>1:
        return float(masse[0])
# Extrahiere Breite von Masse(falls vorhanden)
def masse_b(txt):
    masse=str(txt).replace("cm","").replace(",",".").split("/")
    if len(masse)>1:
        return float(masse[1])

# Extrahiere Höhe von Masse(falls vorhanden)
def masse_h(txt):
    masse=str(txt).replace("cm","").replace(",",".").split("/")
    if len(masse)>1:
        return float(masse[2])

data['Bewertung']=data['Bewertung'].apply(lambda x: round(x * 2) / 2)   #runde zu nächsten Hälfte https://stackoverflow.com/questions/24838629/round-off-float-to-nearest-0-5-in-python Yin Yang
data["Autor"]=data["Autor"].fillna("").apply(lambda x: x.replace("'","´").title()) # Anfang jedes  Autors Namens soll gross geschrieben werden

data["Titel"]=data["Titel"].apply(lambda x: capitalize_first_letter(x))      #es kan passiert das die erste Buchtabe von dem Titel klein ist. Alle Titeln sollen gross geschrieben sein
data["Taschenbuch"]=data["Taschenbuch"].apply(lambda x: preise(x))           #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data["Preis"]=data["Preis"].apply(lambda x: preise(x))                       #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data["Gebundenes Buch"]=data["Gebundenes Buch"].apply(lambda x: preise(x))   #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data['eBook']=data['eBook'].apply(lambda x: preise(x))               #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data['Hörbuch']=data['Hörbuch'].apply(lambda x: preise(x))         #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data["Verlag"]=data["Verlag"].fillna("").apply(lambda x: x.replace("'","´").upper())    # da wir nicht wissen wie richtg der Verlag geschrieen ist wechsel wir alles zum Grossen Buchstaben
data['Gewicht']=data['Gewicht'].apply(lambda x: find_int(x))  #das Gewicht is mit Gramm Einheit, wir wollen aber nur eine Zahl, sehe funktion find int
data['Auflage']=data['Auflage'].apply(lambda x: auflage(x))  # da die Auflage als zb. 1  oder 1.a oder 1. Auflage, muss es angepasst werden
data["Taschenbuch\n                                        (weitere)"] = data["Taschenbuch\n                                        (weitere)"].apply(lambda x: preise(x))  # preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data['Gebundenes Buch\n                                        (weitere)']=data['Gebundenes Buch\n                                        (weitere)'].apply(lambda x: preise(x))               #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data['weitere Ausführungen']=data['weitere Ausführungen'].apply(lambda x: preise(x))               #preis ist in seltsamer string Form, wir wollen nur den float, sehe funktion preise
data['AnzBewerungen']=data['AnzBewerungen'].apply(lambda x: find_int(x))  # da die Auflage als zb. 1  oder 1.a oder 1. Auflage, muss es angepasst werden
data['Originaltitel']=data['Originaltitel'].fillna("").apply(lambda x: x.replace("'","´"))
# zu jeder Zeile in dieser Spalte wird die funktion Auflage genutzt


data['ISBN']=data['ISBN'].apply(lambda x: isbn(x))   #replace"-" - wechsel zum ean als ID
# wenn ISBN fehlt nimm EAN
for i in range(0,len(data)):
    if data.loc[i,"ISBN"]=="nan":  #da wir in der lambda funkciona alles als string behandet haben, ist jetz
                                   # die fehlende Information als string "nan" markiert
        data.loc[i,"ISBN"]=str(int(data.loc[i,"EAN"]))    #wenn ISBN fehlt ersetze mit EAN - da EAN ein float ist
                                                          #muss die Info zum int gewächselt werden, um nachkomma stelle zu vermeiden


data['Erscheinungsdatum']=data['Erscheinungsdatum'].apply(lambda x: datum(x))  #funktion datum oben
data['Übersetzer']=data['Übersetzer'].apply(lambda x: namen(x))         # falls mehrere namen - funktion namen
data['Herausgeber']=data['Herausgeber'].apply(lambda x: namen(x))          # falls mehrere namen - funktion namen
data['Illustrator']=data['Illustrator'].apply(lambda x: namen(x))       # falls mehrere namen - funktion namen


# da die Auflage als zb. 1  oder 1.a oder 1. Auflage, muss es angepasst werden
data['Erscheinungsjahr']=data['Erscheinungsdatum'].apply(lambda x: x.year)     # extrahiere Erschirnungsjahr
data['Erscheinungsmonat']=data['Erscheinungsdatum'].apply(lambda x: x.strftime("%B"))  # extrahiere den Monat
data['IstUebersetzt']=data['Übersetzer'].apply(lambda x: ist(x))                       # prüfe ob es übersetzt ist
data['IstReihe']=data['Reihe'].apply(lambda x: ist(x))                                  # prüfe ob es eine Reihe ist
#data['Maße (L/B/H)'].apply(lambda x: masse_l(x))
data["Laenge"]=data['Maße (L/B/H)'].apply(lambda x: masse_l(x))    # Länge - funktion masse_l
data["Breite"]=data['Maße (L/B/H)'].apply(lambda x: masse_b(x))     # Breite - funktion masse_b
data["Hoehe"]=data['Maße (L/B/H)'].apply(lambda x: masse_h(x))      # Höhe - funktion masse_h

data["Alter"]=data.Erscheinungsjahr.apply(lambda x: 2022-float(x))  #berechne den Buchalter
#preise zum chf


#Umberechne Preise in CHF
data["PreisCHF"]=data["Preis"].apply(lambda x: x*WECHSELKURS_CHF)
data["TaschenbuchCHF"]=data["Taschenbuch"].apply(lambda x: x*WECHSELKURS_CHF)
data["Gebundenes BuchCHF"]=data["Gebundenes Buch"].apply(lambda x: x*WECHSELKURS_CHF)
data['eBookCHF']=data['eBook'].apply(lambda x: x*WECHSELKURS_CHF)
data['HörbuchCHF']=data['Hörbuch'].apply(lambda x: x*WECHSELKURS_CHF)
#Umbennen Spalten
data.rename(columns = {'Gebundenes Buch\n                                        (weitere)':'Gebundenes Buch (weitere)','Taschenbuch\n                                        (weitere)': 'Taschenbuch (weitere)'}, inplace = True)


#schreibe csv
data.to_csv("../Data/thalia_stage3.csv")

