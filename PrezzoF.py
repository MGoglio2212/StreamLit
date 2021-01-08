# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 13:09:08 2020

@author: gogliom
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 19:25:26 2020

@author: gogliom
"""
filename = "Eni_link_CE_lucegaspdf.pdf"

#Doc = r"D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Acea_FastClick_CE.pdf"
#Doc = convert_pdf_to_txt(Doc)
#Doc = Doc.upper()


import pandas as pd
import re

def PrezzoComponenteEnergiaF1(Doc):
    
    PossiblePrice = []
    Base = []
    
    
    #le inserisco come regular expression perchè non so quanti spazi ci sono e se magari c'è una new line (\s+)
    r1 = 'F1'
    regex = [r1]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
    
    
    
    #prendo i numeri positivi  
    #regexNum1 = r'-?\d*\,.?\d+'
    #regexNum2 = r'-?\d*\..?\d+'
    
    regexNum1 = r'\d+\,?\d+'
    regexNum2 = r'\d+\.?\d+'
    
    
    regexNum = [regexNum1, regexNum2]
    
    regexNum = re.compile('|'.join(regexNum))
    
    
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    #converto in numero
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri < 1 e positivi
    PossiblePrice = PossiblePrice[(PossiblePrice['Price_NUM'] > 0) & (PossiblePrice['Price_NUM'] < 1)]
    
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
    Prezzo = Prezzo[Prezzo['dist'] > - 15]
    #AD OGNI MODO NELLE PRIORITA' PRENDO IL PIU PICCOLO IN VALORE ASSOLUTO
    Prezzo['dist'] = Prezzo['dist'].abs()
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')
    
   
    print(Prezzo['Price'])
    return Prezzo['Price'] 


def PrezzoComponenteEnergiaF2(Doc):
    
    PossiblePrice = []
    Base = []
    

    
    #le inserisco come regular expression perchè non so quanti spazi ci sono e se magari c'è una new line (\s+)
    r1 = 'F2'
    r2 = 'F23'
    regex = [r1, r2]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
    
    
    
    #prendo i numeri positivi  
    #regexNum1 = r'-?\d*\,.?\d+'
    #regexNum2 = r'-?\d*\..?\d+'
    
    regexNum1 = r'\d+\,?\d+'
    regexNum2 = r'\d+\.?\d+'
    
    
    regexNum = [regexNum1, regexNum2]
    
    regexNum = re.compile('|'.join(regexNum))
    
    
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    #converto in numero
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri < 1 e positivi
    PossiblePrice = PossiblePrice[(PossiblePrice['Price_NUM'] > 0) & (PossiblePrice['Price_NUM'] < 1)]
    
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
    Prezzo = Prezzo[Prezzo['dist'] > - 15]
    #AD OGNI MODO NELLE PRIORITA' PRENDO IL PIU PICCOLO IN VALORE ASSOLUTO
    Prezzo['dist'] = Prezzo['dist'].abs()
    
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')
    
   
    print(Prezzo['Price'])
    return Prezzo['Price'] 




def PrezzoComponenteEnergiaF3(Doc):
    
    PossiblePrice = []
    Base = []
    
    
    #le inserisco come regular expression perchè non so quanti spazi ci sono e se magari c'è una new line (\s+)
    r1 = 'F3'
    r2 = 'F23'
    regex = [r1, r2]
    
    regex = re.compile('|'.join(regex))
    
    
    Base = [m.start() for m in regex.finditer(Doc)]
    Base = pd.DataFrame(Base, columns = ['PositionBase'])
    
    
    
    #prendo i numeri positivi  
    #regexNum1 = r'-?\d*\,.?\d+'
    #regexNum2 = r'-?\d*\..?\d+'
    
    regexNum1 = r'\d+\,?\d+'
    regexNum2 = r'\d+\.?\d+'
    
    
    regexNum = [regexNum1, regexNum2]
    
    regexNum = re.compile('|'.join(regexNum))
    
    
    NumberPos = [m.start() for m in regexNum.finditer(Doc)]
    NumberValue = regexNum.findall(Doc)
    NumberTuples = list(zip(NumberValue,NumberPos))
    
    
    PossiblePrice = pd.DataFrame(NumberTuples, columns=['Price', 'Position'])
    #converto in numero
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price.replace(",","."), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: row.Price_NUM.replace(" ",""), axis = 1)
    PossiblePrice['Price_NUM'] = PossiblePrice.apply(lambda row: float(row.Price_NUM), axis = 1)
    
    #filtro numeri < 1 e positivi
    PossiblePrice = PossiblePrice[(PossiblePrice['Price_NUM'] > 0) & (PossiblePrice['Price_NUM'] < 1)]
    
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
    Prezzo = Prezzo[Prezzo['dist'] > - 15]
    #AD OGNI MODO NELLE PRIORITA' PRENDO IL PIU PICCOLO IN VALORE ASSOLUTO
    Prezzo['dist'] = Prezzo['dist'].abs()
    
    
    Prezzo = Prezzo.nsmallest(1, 'dist')
    
   
    print(Prezzo['Price'])
    return Prezzo['Price'] 
