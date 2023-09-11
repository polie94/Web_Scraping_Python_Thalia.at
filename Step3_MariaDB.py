import mariadb
import mysql.connector
import pandas as pd
import numpy as np
### VON https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
conn = mysql.connector.connect(user='cip_user', password='cip_pw', host='127.0.0.1', database='CIP')
cur = conn.cursor()

data= pd.read_csv("../Data/thalia_stage3.csv")
# Die daten sollen als Objekte gespeichert werden. Falls es nan gibt sollen sie mit dem Text "NULL" ersetzt werden
data=data.astype(object).replace(np.nan, 'NULL')

#Umbennen Spalten
#data.columns = data.columns.str.replace('Gebundenes Buch\n                                        (weitere)', 'Gebundenes Buch (weitere)')
#data.rename(columns = {'Gebundenes Buch\n                                        (weitere)':'Gebundenes Buch (weitere)','Taschenbuch\n                                        (weitere)': 'Taschenbuch (weitere)'}, inplace = True)
# Erstelle Tabelle falls keine existiert
cur.execute("CREATE TABLE IF NOT EXISTS thalia(ISBN_EAN bigint PRIMARY KEY,Autor varchar(255) NULL,Titel varchar(255) NULL, Bewertung float NULL, Preis float NULL,Gebundenes_Buch float  NULL, Taschenbuch  float NULL, eBook float  NULL, Verkaufsrang int NULL, Einband varchar(64) NULL,Erscheinungsdatum date NULL, \
        Verlag varchar(124) NULL,Seitenzahl int NULL, MasseLBH varchar(48) NULL, Gewicht int NULL, Auflage varchar(48) NULL,Origialtitel varchar(255) NULL, Uebersetzer varchar(255) NULL,Sprache varchar(255) NULL, Reihe  varchar(255) NULL, Hoerbuch float NULL, \
        Gebundenes_Buch_weitere float NULL, Altersempfehlung varchar(126) NULL, Taschenbuch_weitere float NULL, Herausgeber varchar(255) NULL, WeitereAusfuehrungen float NULL, Illustrator varchar(255) NULL, \
        MasseLB varchar(124) NULL, Abbildungen varchar(255) NULL,Erscheinungsjahr year NULL,Erscheinungsmonat varchar(32) NULL,IstUebersetzt varchar(4) NULL, IstReihe varchar(4) NULL, \
        Laenge float NULL, Breite float NULL, Hoehe float NULL, PreisCHF float NULL, TaschenbuchCHF float NULL,Gebundenes_BuchCHF float  NULL, eBookCHF float NULL,HoerbuchCHF float NULL) ;")

#insert die Daten von DF in MariaDB zeilenweise.
for i in range(0,len(data)):

     text=f"INSERT INTO thalia (ISBN_EAN,Autor,Titel,Bewertung,Preis,Gebundenes_Buch,Taschenbuch,eBook,Verkaufsrang,Einband,Erscheinungsdatum,Verlag,Seitenzahl, MasseLBH,Gewicht, Auflage,Origialtitel,Uebersetzer,Sprache,Reihe,  \
             Hoerbuch,Gebundenes_Buch_weitere,Altersempfehlung, Taschenbuch_weitere, Herausgeber, WeitereAusfuehrungen, Illustrator, MasseLB , Abbildungen,Erscheinungsjahr,Erscheinungsmonat,IstUebersetzt, IstReihe,  \
            Laenge,Breite, Hoehe, PreisCHF, TaschenbuchCHF,Gebundenes_BuchCHF, eBookCHF,HoerbuchCHF) \
             VALUES({data.loc[i,'ISBN']},'{data.loc[i,'Autor']}','{data.loc[i,'Titel']}',{data.loc[i,'Bewertung']},{data.loc[i,'Preis']},{data.loc[i,'Gebundenes Buch']},{data.loc[i,'Taschenbuch']},{data.loc[i,'eBook']}, \
                {data.loc[i,'Verkaufsrang']},'{data.loc[i,'Einband']}','{data.loc[i,'Erscheinungsdatum']}','{data.loc[i,'Verlag']}',{data.loc[i,'Seitenzahl']} ,'{data.loc[i,'Maße (L/B/H)']}',{data.loc[i,'Gewicht']}, \
               '{data.loc[i,'Auflage']}','{data.loc[i,'Originaltitel']}' ,'{data.loc[i,'Übersetzer']}','{data.loc[i,'Sprache']}','{data.loc[i,'Reihe']}',{data.loc[i,'Hörbuch']},{data.loc[i,'Gebundenes Buch (weitere)']},\
                 '{data.loc[i,'Altersempfehlung']}', {data.loc[i,'Taschenbuch (weitere)']},'{data.loc[i,'Herausgeber']}',{data.loc[i,'weitere Ausführungen']},'{data.loc[i,'Illustrator']}', \
                 '{data.loc[i,'Maße (L/B)']}','{data.loc[i,'Abbildungen']}','{data.loc[i,'Erscheinungsjahr']}','{data.loc[i,'Erscheinungsmonat']}','{data.loc[i,'IstUebersetzt']}', '{data.loc[i,'IstReihe']}', \
                 {data.loc[i, 'Laenge']},{data.loc[i,'Breite']}, {data.loc[i,'Hoehe']}, {data.loc[i,'PreisCHF']}, {data.loc[i,'TaschenbuchCHF']}, \
                  {data.loc[i,'Gebundenes BuchCHF']},{data.loc[i,'eBookCHF']}, {data.loc[i,'HörbuchCHF']});"

     print(text)
     cur.execute(text)
#schliesse die Transaktion
conn.commit()
