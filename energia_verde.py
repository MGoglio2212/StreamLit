# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 11:05:18 2020

@author: fiaria
"""

""" lists environment variables, and splits elements in path variable """

EON = convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\E.ON_Luce_Insieme_Web30.pdf").upper()
ACEA= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\Acea_Come_Noi_CE_DOM.pdf").upper()
ENI= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\EniSceltaSicura.pdf").upper()
ENEL1= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\EnelE-Light_cte.pdf").upper()
ENEL2= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\EnelLuce30.pdf").upper()
ENGIE= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\Energia3.0Light.pdf").upper()
ABENERGIE= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\ABEnergie6MesiGreenLuce.pdf").upper()
SORGENIA= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\SorgeniaLuce.pdf").upper()
IBERDROLA= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\IberdrolaEcoChiara.pdf").upper()
ENERGIT= convert_pdf_to_txt(r"C:\Users\fiaria\Desktop\ENERGY OFFER RECOGNITION\CTE\Energit-Casa-Web.pdf").upper()


import pandas as pd
import re
 
'''
Questo approccio consente di estrarre direttamente la parte di testo che contiene il termine ricercato.
Non andrei di "or" se non per declinazioni diverse della stessa parola su singolari o plurali, piuttosto che femminili o maschili.
il testo estratto dalla regex può essere processato con altra regex che trova magari i prezzi o la componente percentuale di energie rinnovabili 

'''
   
Regex1 = '[^.]* RINNOVABILI [^.]*\. | [^.]* RINNOVABILE [^.]*\. '    
p = re.compile(Regex1)
result = p.findall(ABENERGIE)
result


'''
Questo approccio, lo stesso utilizzato per capire se il prezzo era variabile o meno, consente di estrarre le frasi che contengono tutti i termini ricercati, 
anche non in sequenza. Il problema in questo caso è che va passato il testo riga per riga, magari tenendo solo le righe con cui c'è match,
per poi trovare magari i prezzi o la componente percentuale di energie rinnovabili 

''' 

Regex2= r'^(?=.*\bESCLUSIVAMENTE\b)(?=.*\bRINNOVABILI\b).*$'
c = re.compile(Regex2)
Price_green_explaination= []
for i in ENERGIT.split('\n'):
    if c.match(i):
        Price_green_explaination.append(i)
Price_green_explaination


'''
Questo approccio puntuale lo stavo testando, giacchè i due precedenti non funzionano bene su tutte le CTE

'''

r1 = 'ENERGIA\s+VERDE\s+'
r2 = '100%\s+FONTI\s+RINNOVABILI'
r3 = 'ENERGIA\s+VERDE\s+100%'
r4 = 'ENERGIAVERDE'

regex = [r1, r2, r3, r4]
    
regex = re.compile('|'.join(regex))
regex

