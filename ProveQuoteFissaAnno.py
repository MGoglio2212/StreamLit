# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:20:01 2020

@author: gogliom
"""



######
# PROVO A RECUPERARE PREZZO MATERIA PRIMA:
# CERCO TUTTE OCCORRENZE DI €/KWH ED ESTRAGGO PAROLA PRECEDENTE
# CERCO UNA LISTA DI POSSIBILI MODI CON CUI CHIAMARLO 
# CREO UN CARTESIANO E CALCOLO DISTANZA TRA OGNI POSSIBILE COPPIA
# PRENDO VALORE CON DISTANZA MINORE 


#Doc = "D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\ABEnergie6MesiGreenLuce.pdf"
##### BISOGNA IMPORTARE FUNZIONE CONVERT_PDF_TO_TEXT DA ALTRO PROGRAMMA!


#Doc = r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Acea_FastClick_CE.pdf"
#Doc = convert_pdf_to_txt(Doc)
#Doc = Doc.upper()




import pandas as pd
import re
from ProvePDF import convert_pdf_to_txt
import numpy as np
import regex as re  #ATTENZIONE! DEVO IMPORTARE 3RD PARTY REGEX MODULO PERCHè QUESTO SUPPORTA I "NEGATIVE LOOKAHEAD
                    #DI LUNGHEZZA VARIABILE --> DEVO PRENDERE "VERDE" CHE NON SIA PRECEDUTO DA NUMERO O DA N° E QUESTO 
                    #E' UN NEGATIVE LOOKAHEAD DI LUNGHEZZA VARIABILE CHE VA IN ERRORE SU MODULO STANDARD DI RE
                    #CFR (https://www.reddit.com/r/learnpython/comments/d5g4ow/regex_match_pattern_not_preceded_by_either_of_two/)
def PrezzoComponenteCommVendita(Doc):
    
    PossiblePrice_CV = []
    Base_CV = []
    
    #Doc = convert_pdf_to_txt(Doc)
    #Doc = Doc.upper()
    
    #le inserisco come regular expression perchè mettendo . come any character (spezi,"E", a capo..)
    r1 = 'PREZZO.{0,10}COMMERCIALIZZAZIONE.{0,10}VENDITA'
    r2 = 'COSTI.{0,10}COMMERCIALIZZAZIONE'
    r3 = 'PCV'
    r5 = 'COMMERCIALIZZAZIONE.{0,10}VENDITA'
    r6 = 'CORRISPETTIVO.{0,10}COMMERCIALIZZAZIONE'
    
    #introdotte per il gas
    r4 = '(?<!MATERIA PRIMA.{1,80})QVD'


    regex_CV = [r1,r2,r3, r4, r5,r6]
    
    regex_CV = re.compile('|'.join(regex_CV))
    
    
    Base_CV = [m.start() for m in regex_CV.finditer(Doc)]
    Base_CV = pd.DataFrame(Base_CV, columns = ['PositionBase'])
    

    
    
    #r1 = '-?\d*,?\d+\s'
    #r2 = '-?\d*\.?\d+\s'

    r1 = '(?<!ARTICOLO.{0,10})-?\s+\d*,?\d+\s'
    #r2 = '-?\s\d*\.?\d+\s'
    r3 = '(?<!ARTICOLO.{0,10})-?\s+\d*,?\d+€'
    #r4 = '-?\s\d*\.?\d+€'
   

    regex_Num = [r1,r3]
    
    regexNum_CV = re.compile('|'.join(regex_Num))
    
    #prendo i numeri eventualmente decimali
    NumberPos_CV = [m.start() for m in regexNum_CV.finditer(Doc)]
    NumberValue_CV = regexNum_CV.findall(Doc)
    NumberTuples_CV = list(zip(NumberValue_CV,NumberPos_CV))
    
    
    PossiblePrice_CV = pd.DataFrame(NumberTuples_CV, columns=['Price', 'Position'])
    #converto in numero    
    PossiblePrice_CV['Price_NUM'] = PossiblePrice_CV.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice_CV['Price_NUM'] = PossiblePrice_CV.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice_CV['Price_NUM'] = PossiblePrice_CV.apply(lambda row: row.Price_NUM.replace("€",""), axis = 1)
    PossiblePrice_CV['Price_NUM'] = PossiblePrice_CV.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri > 10 e positivi
    PossiblePrice_CV = PossiblePrice_CV[(PossiblePrice_CV['Price_NUM'] > 5) & (PossiblePrice_CV['Price_NUM'] < 200) ]
    
    #verifico se nei 40 caratteri prima o dopo c'è riferimento a mese o anno 
    PossiblePrice_CV['Intorno'] = PossiblePrice_CV.apply(lambda row: Doc[row.Position-40:row.Position+40], axis = 1)
    PossiblePrice_CV['Mese'] = np.where(PossiblePrice_CV['Intorno'].str.contains('MESE'),1,
                                    np.where(PossiblePrice_CV['Intorno'].str.contains('MENSIL'),1,
                                             0))
    PossiblePrice_CV['Anno'] = np.where(PossiblePrice_CV['Intorno'].str.contains('ANNO'),1,
                                    np.where(PossiblePrice_CV['Intorno'].str.contains('ANNUAL'),1,
                                             0))

    
    '''
    APPROCCIO IN BASE AL QUALE CERCO €/KWH E PRENDO PAROLA PRECEDENTE, MA IN ALCUNI CASI NELLE TABELLE NON E ESPLICITATA
    EURO/KWH VICINO AL NUMERO
    ii = 0
    for ww in Doc.split():
        if "€/KWH" in ww or "EURO/KWH" in ww:
            pw = Doc.split()[ii-1]
            po = Doc.find(Doc.split()[ii-1]+" "+Doc.split()[ii])
            nn = pd.DataFrame({'Price': [pw], 'Position': [po]})
            PossiblePrice = PossiblePrice.append(nn) 
            #Positions = Positions + list(ii-1)        
        ii = ii + 1 
    #estraggo i numeri 
    PossiblePrice['Price'] = PossiblePrice.apply(lambda row: re.findall('-?\d*\,.?\d+', str(row.Price)), axis=1)
    #elimino eventuali stringe vuote
    PossiblePrice = PossiblePrice[PossiblePrice['Price'].apply(lambda row: len(row)) > 0]
    '''
    

    
    Base_CV['key'] = 0
    PossiblePrice_CV['key'] = 0
    
    Prezzo_CV = Base_CV.merge(PossiblePrice_CV, how='outer')
    Prezzo_CV['dist'] = Prezzo_CV.apply(lambda row: row.Position - row.PositionBase, axis = 1)
    #FILTRO PER LE DISTANZE POSITIVE (IL NUMERO VIENE DOPO LA PAROLA, OPPURE NEGATIVE MOLTO PICCOLE DOVE QUINDI LA BASE VIENE IMMEDIATAMENTE DOPO )
    Prezzo_CV = Prezzo_CV[(Prezzo_CV['dist'] > - 35) & (Prezzo_CV['dist'] < 200)]
    
    

    
    Prezzo_CV = Prezzo_CV.nsmallest(1, 'dist')
    #trovo sia mese che anno, filtro in base a valore
    if Prezzo_CV['Mese'].iloc[0] == 1 and Prezzo_CV['Anno'].iloc[0] == 1:
        if Prezzo_CV['Price_NUM'].iloc[0] > 15:
            Prezzo_CV['Price'] = Prezzo_CV['Price'] + " anno"    
        else:
            Prezzo_CV['Price'] = Prezzo_CV['Price'] + " mese"    
    #trovo solo mese
    elif Prezzo_CV['Mese'].iloc[0] == 1:
        Prezzo_CV['Price'] = Prezzo_CV['Price'] + " mese"    
        
    #trovo solo anno
    elif Prezzo_CV['Anno'].iloc[0] == 1:
        Prezzo_CV['Price'] = Prezzo_CV['Price'] + " anno"
        
    #non trovo niente
    else:
        if Prezzo_CV['Price_NUM'].iloc[0] > 15:
            Prezzo_CV['Price'] = Prezzo_CV['Price'] + " anno"    
        else:
            Prezzo_CV['Price'] = Prezzo_CV['Price'] + " mese"    
        

    
    return Prezzo_CV['Price']




def PrezzoComponenteDispacciamento(Doc):
    
    PossiblePrice = []
    Base = []
    
    #Doc = convert_pdf_to_txt(Doc)
    #Doc = Doc.upper()
    
    #le inserisco come regular expression perchè mettendo . come any character (spezi,"E", a capo..)
    r1 = 'PREZZO.+DISPACCIA'
    r2 = 'COSTI.+DISPACCIA'
    r3 = 'COMPONEN.+DISPACCIA'
    
    
    
    regex = [r1,r2,r3]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
    
    
    
    r1 = '-?\s\d*,?\d+\s'
    r2 = '-?\s\d*\.?\d+\s'
    r3 = '-?\s\d*,?\d+€'
    r4 = '-?\s\d*\.?\d+€'
    

    #r1 = '-?\d*,?\d+'
    #r2 = '-?\d*.?\d+'

    regex_Num = [r1,r2,r3,r4]
    
    regexNum_DIS = re.compile('|'.join(regex_Num))

    NumberPos = [m.start() for m in regexNum_DIS.finditer(Doc)]
    NumberValue = regexNum_DIS.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    #converto in numero

    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace("€",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri > - 30 (possono essere negativi..)
    PossiblePrice = PossiblePrice[(PossiblePrice['Price_NUM'] > -30) & (PossiblePrice['Price_NUM'] < 100)]
    
    '''
    APPROCCIO IN BASE AL QUALE CERCO €/KWH E PRENDO PAROLA PRECEDENTE, MA IN ALCUNI CASI NELLE TABELLE NON E ESPLICITATA
    EURO/KWH VICINO AL NUMERO
    ii = 0
    for ww in Doc.split():
        if "€/KWH" in ww or "EURO/KWH" in ww:
            pw = Doc.split()[ii-1]
            po = Doc.find(Doc.split()[ii-1]+" "+Doc.split()[ii])
            nn = pd.DataFrame({'Price': [pw], 'Position': [po]})
            PossiblePrice = PossiblePrice.append(nn) 
            #Positions = Positions + list(ii-1)        
        ii = ii + 1 
    #estraggo i numeri 
    PossiblePrice['Price'] = PossiblePrice.apply(lambda row: re.findall('-?\d*\,.?\d+', str(row.Price)), axis=1)
    #elimino eventuali stringe vuote
    PossiblePrice = PossiblePrice[PossiblePrice['Price'].apply(lambda row: len(row)) > 0]
    '''
    
    
    
    Base['key'] = 0
    PossiblePrice['key'] = 0
    
    Prezzo = Base.merge(PossiblePrice, how='outer')
    Prezzo['dist'] = Prezzo.apply(lambda row: row.Position - row.PositionBase, axis = 1)
    #FILTRO PER LE DISTANZE POSITIVE (IL NUMERO VIENE DOPO LA PAROLA, OPPURE NEGATIVE MOLTO PICCOLE DOVE QUINDI LA BASE VIENE IMMEDIATAMENTE DOPO )
    Prezzo = Prezzo[Prezzo['dist'] > - 10]
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')
    
    print(Prezzo)
    return Prezzo['Price']
