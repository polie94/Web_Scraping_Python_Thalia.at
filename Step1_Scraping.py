import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd
import asyncio
from selenium.webdriver.common.action_chains import ActionChains
#from requests_html import HTMLSession as r
from selenium.webdriver.common.keys import Keys

##Funktion

###scraping vom einzelnen Buch
def scrap_book(link):
    #Einstellen von User-Agent
    my_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"  ## gepüfft auf https://www.whatsmyua.info/
    link_to_shop = "https://www.thalia.at" + link
    opts = Options()
    opts.add_argument("user-agent=" + my_ua)
    driver = webdriver.Chrome(options=opts)
    driver.get(link_to_shop)

    # kombiniere Selenium with Beautifulsoup
    page_source = driver.page_source  #https://medium.com/ymedialabs-innovation/web-scraping-using-beautiful-soup-and-selenium-for-dynamic-page-2f8ad15efe25
    soup = BeautifulSoup(page_source, 'lxml') #https://stackoverflow.com/questions/36505469/beautiflsoup-create-soup-with-a-snippet-of-page-source


    driver.maximize_window()
    ###wegklikcken von den ersten Pop-ups (Cookies und Benachrichtigung)
    wait = WebDriverWait(driver, 15)
    try:
        #Warte bis Cookies Button lässt sich anklicken
        cookie_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="element-button-primary-variant button-zustimmen"]')))  #https://selenium-python.readthedocs.io/waits.html
        cookie_button.click()
    except:
        print("already clicked")

    driver.implicitly_wait(1)  #warte
    try:
        # Warte bis Benachrichtigung Button lässt sich anklicken
        benachrichtigung_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="btn btn-secondary gb-push-denied"]')))

        benachrichtigung_button.click()
    except:
        print("already clicked")

    ### Scrapping von Buch relevanten Informationen
    titel = driver.find_element(by=By.XPATH, value='//*[@class="element-headline-large titel"]').text

    #Manche Bücher haben keinen Autor, Bewertung deswegen "Try", wenn es keinen Autor gibt schreibe respektiv einen leeren String
    try:
        autor = driver.find_element(by=By.XPATH, value='//*[@interaction="autor-klick"]').text
    except:
        print("Kein Autor")
        autor = ""
    try:
        bewertung = soup.find('span', class_='current-rating').text

    except:
        print("Keine Bewertung")
        bewertung = ""
    # Hier wird der Hauptpreis geholt. Es gibt zwei mglichkeiten: Das Buch hat einen reguleren Preis oder ist reduziert. Wenn es reduziert ist
    # solle man den "durchgestrichenen" (reguleren) nehmen.
    try:
        preis=soup.find(['p','s'], class_=['element-headline-medium','element-text-small streichpreis']).text

    except:
        print("Kein Preis")
        preis=""

    #Scrape Bewertung. Wenn keine, schreib einen leeren String
    try:
        anz_bewert=soup.find(['p'], class_=['element-text-standard-strong rating-summray-text']).text

    except:
        print("Keine Bewertung")
        anz_bewert=""
    # Vorhandene Infos zusammenführen in eine Dictionary
    book_list = {"Link":link_to_shop, 'Autor': autor, 'Titel': titel, "Bewertung": bewertung, "Preis":preis, "AnzBewerungen":anz_bewert}

    #Scrapen von Arten vom Buch, wie eBook, Hörbuch  (andere Buchoptionen, die vorhanden sind)
    #Es ist möglich, dass es beliebig viele gibt. Alle Arten sind in eine Liste hinzugefügt.
    buch_bezeichnung_klein = []
    buch_bezeichnung = soup.find_all('p', class_='element-text-small bezeichnung')
    buch_bezeichnung_v = [item.text.rstrip('\r\n').lstrip('\r\n').strip() for item in buch_bezeichnung]

    # Scrapen von Arten vom Buch, wie eBook, Hörbuch  (andere Buchoptionen, die vorhanden sind)
    # Es ist möglich, dass es beliebig viele gibt. Die preisen sind in der Klasse "element-text-small-strong". Wenn
    # man aber scrapt nach dieser Klasse, kommen auch die Informationen die in der Klasse 'element-text-small-strong niedrigster-preis' enthalten sind
    # in der Liste buch_bezeichnung_klein_preis werden nur die Preise genommen, die in der Klasse 'element-text-small-strong' hochkommen,
    # und nicht in 'element-text-small-strong niedrigster-preis'
    buch_bezeichnung_klein_preis = []
    list1 = soup.find_all('strong', class_='element-text-small-strong')
    list2 = soup.find_all('strong', class_='element-text-small-strong niedrigster-preis')
    buch_bezeichnung_klein_preis = [x for x in list1 if x not in list2]
    buch_bezeichnung_klein_preis_v = [item.text.rstrip('\r\n').lstrip('\r\n').strip() for item in
                                      buch_bezeichnung_klein_preis]

    #Es wird eine Dictionary erstelte, welche Preise dem Buchtyp zuordnet
    klein = dict(zip(buch_bezeichnung_v, buch_bezeichnung_klein_preis_v))
    #Die Dictionary über die Bücher wird mit den neuen Informationen aktualisiert.
    book_list.update(klein)

    # details=soup.find_all(['dialog'], class_=['element-overlay-slide-in'])

    #Die Details sind die Informationen, die erscheinen, wenn die Schaltfläche "Weitere Details" angecklickt wird.
    #Die Informationen sind normal (ohne die Schaltfläche anzuklicken) für den Leser nicht siehtbar. Aber sind im HTML vorhanden.
    details = soup.find_all(['dialog'], class_=['element-overlay-slide-in'])

    key = ""
    val = ""

    #Erstmal werden die Bezeichnungen (z.B. Herausgeber oder Erscheinungsjahr) geholt und in eine Key-Liste hinzugefügt
    for item in details:
        key = item.find_all('h3', class_='element-text-standard-strong detailbezeichnung')

    keys = [item.text.rstrip('\r\n').lstrip('\r\n').strip() for item in key] # mit kleiner Bereinigung

    vals = []
    section = []
    element = []

    # Hier werden die Informationen über den respektiven Werten gescrapt. Erstnmal teilen wir die Daten je nach Section.
    # Weiter jede Section wird geprüfft, ob es ein normaler Text( Klasse: "element-text-standard single-value" ), eine Liste(Klasse: ""values-list")
    # oder ein Link(Klasse: "element-link-standard") hat. Wenn es  den Text oder den Link enthällt, wird der jeweillige Text geholt.
    # Falls es eine Liste ist, wird es geprüfft, ob die Elemente Texten oder Links sind. Für die beider Fälle wird ein String von den Elementen vorbereitet.
    # Alle Werte werden in eine Liste vals gespeichert.
    for item in details:
        section = item.find_all("section", class_='artikeldetail')
    for elem in section:
        if elem.find(['p'], class_=["element-text-standard single-value"]):
            vals.append(elem.find(['p'], class_=["element-text-standard single-value"]).text)

        elif elem.find(['ul'], class_=["values-list"]):
            if elem.find_all(['a'], class_=["element-link-standard"]):
                ref = elem.find_all(['a'], class_=["element-link-standard"])
                vals.append(", ".join([x.text for x in ref]))
                continue
            if elem.find_all(['li'], class_=["element-text-standard value"]):
                ref = elem.find_all(['li'], class_=["element-text-standard value"])
                vals.append(", ".join([x.text for x in ref]))
                continue
        elif elem.find(['a'], class_=["element-link-standard"]):
            vals.append(elem.find(['a'], class_=["element-link-standard"]).text)

    #Die Details werden in eine neue Dictionary gespeichert (details). Z.b Erscheinungsdatum: "2022-10-10"
    details = dict()
    for key, val in zip(keys, vals):
        details[key] = val

    #Die Dicktionary über das Buch wird mit den Details upgedatet.
    book_list.update(details)
    print(book_list)

    #Die Seite wird geschlossen.
    driver.close()

    return book_list


list_of_books=[]

# nutze eigenen user agent
my_ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36" ## gepüfft auf https://www.whatsmyua.info/
opts = Options()
opts.add_argument("user-agent="+my_ua)
driver = webdriver.Chrome(chrome_options=opts)
driver.get("https://www.thalia.at/kategorie/schweiz-17894/")
driver.maximize_window()
###wegklikcken von den ersten Pop-ups (Cookies und Benachrichtigung)
wait = WebDriverWait(driver, 15)

#Wegklichen von Pop-Ups Windows - Cookies
try:
    cookie_button=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="element-button-primary-variant button-zustimmen"]')))
    time.sleep(random.randint(0,1)*5) #zufallsnummer - warte zeit sollte normal verteilt werden
                                                # und einen echten user gut simulieren
    cookie_button.click()
except:
    print("kein Cookie")

driver.implicitly_wait(1)
#Wegklichen von Pop-Ups Windows - Benachrichtigung

try:
    benachrichtigung_button=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="btn btn-secondary gb-push-denied"]')))
    time.sleep(random.randint(0,1)*10)
    benachrichtigung_button.click()
except:
    print("Keine Benachrichtigung")

# kombiniere Selenium with Beautifulsoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
nachladen=0
href_last = set()  # set von bereits bearbeiteten Links
read=0 #check

#Scrollen, Linksammeln und Linksöffnen
while(True):
    driver.execute_script("window.scrollBy(0,1080)", "") ## scroll runter
    time.sleep(1)
    anz_sichtbar=int(driver.find_element(by=By.XPATH, value='//*[@class="sichtbare-artikel"]').text)  # speicher die anzahl sichtbarer Elemente
    anz_treffer=int(driver.find_element(by=By.XPATH, value='//*[@class="anzahl-treffer"]').text)         # speicher die anzahl aller Elemente
    print(anz_treffer)
    #wenn der Button "Weitere Ergebnisse..." sichtbar und activ ist :
    if driver.find_element(by=By.XPATH,value='//*[@interaction="weitere-ergebnisse-laden"]').is_enabled() &driver.find_element(by=By.XPATH,value='//*[@interaction="weitere-ergebnisse-laden"]').is_displayed() and anz_sichtbar<anz_treffer:
        soup1=BeautifulSoup(driver.page_source,"html.parser")

        liste = []
        #Finde alle Produkte
        liste = soup1.find_all('li', { 'class':'tm-produktliste__eintrag', 'product-position': True})
        href_new=set() #set für die sichtbare Links.Ermöglicht das Ausfiltern von verdoppelten Links. Verurscht,dass die Reihenfolge von Bücher nicht eingehalten ist.
        for elem in liste:

            # src=elem.find("a", class_="element-link-toplevel tm-produkt-link",href=True)["href"]
            #Aktualisiere die Liste von neuen Links
            href_new.add(elem.find("a", class_="element-link-toplevel tm-produkt-link",href=True)["href"])


        href_to_read=href_new-href_last  #Die Links zum Lesen sin die, die neu gelesen waren
        href_last=href_new  #die Menge von bereits gelesenen  Links wird mit den neuen Links aktualisiert.
        #scrap die Bücher aufgrund von dem Link zum Lesen
        for src in href_to_read:
            read+=1
            print(read)
            list_of_books.append(scrap_book(src))

        time.sleep(1)
        #scroll hoch, dann kliche den Button an, um die neue Bücher zu sehen
        driver.execute_script("window.scrollBy(0,-1080)", "")
        driver.execute_script("window.scrollBy(0,-1080)", "")
        driver.find_element(by=By.XPATH, value='//*[@interaction="weitere-ergebnisse-laden"]').click()
        time.sleep(1)
    # Es kann passieren, dass das Program zum Seitenende gescrollt hat, aber nicht alle Produkte geladen wurden.
    #In diesem Fall soll das Programm 4 mal nach oben scrollen und dann normall in der whil schleife runter zu scrollen
    if anz_sichtbar < anz_treffer and driver.execute_script(
            "if((window.innerHeight+window.scrollY)>=document.body.offsetHeight){return true;}"):  # execute script: https://stackoverflow.com/questions/33905684/how-to-tell-bottom-of-page-has-been-reached  von Hans VK
        driver.execute_script("window.scrollBy(0,-1080)", "")
        driver.execute_script("window.scrollBy(0,-1080)", "")
        driver.execute_script("window.scrollBy(0,-1080)", "")
        driver.execute_script("window.scrollBy(0,-1080)", "")
    # Wenn alle Produkte geladen sind und das Programmm ist am Seitenende
    if anz_sichtbar == anz_treffer and driver.execute_script(
            "if((window.innerHeight+window.scrollY)>=document.body.offsetHeight){return true;}"):


        soup1 = BeautifulSoup(driver.page_source, "html.parser")

        liste = []
        # Finde alle Produkte
        liste = soup1.find_all('li', {'class': 'tm-produktliste__eintrag', 'product-position': True})
        href_new = set()
        for elem in liste:
           # src = elem.find("a", class_="element-link-toplevel tm-produkt-link", href=True)["href"]
            # Aktualisiere die Liste von neuen Links
            href_new.add(elem.find("a", class_="element-link-toplevel tm-produkt-link", href=True)["href"])

        href_to_read = href_new - href_last #Die Links zum Lesen sin die, die neu gelesen waren
        href_last = href_new  #die Menge von bereits gelesenen  Links wird mit den neuen Links aktualisiert.
        #scrap die Bücher aufgrund von dem Link zum Lesen
        for src in href_to_read:
            list_of_books.append(scrap_book(src))


        #Speicher die Liste von Dictionaries als Pandas DF und dann schreibe es in eine CSV Datei.
        pd.DataFrame.from_dict(list_of_books).to_csv("../Data/thalia_stage1.csv")
        break








