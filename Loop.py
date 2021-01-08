# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 11:01:16 2020

@author: gogliom
"""
import os
os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\App\Funzioni")

import re
import numpy as np

from ProvePDF import convert_pdf_to_txt 
from LetturaPdf import read_pdf  #importazione basata sul pacchetto che tiene struttura
from LetturaPdf_2 import read_pdf_2 #importaizone basata sulla convert_pdf_to_txt e poi splittata in ele / gas in base ai paragrafi


from ProveDurata import Durata
from ProveQuoteFissaAnno import PrezzoComponenteDispacciamento , PrezzoComponenteCommVendita 
from ProveScadenza import Scadenza 
from Detect_PrezzoMonorario import PrezzoComponenteEnergia
from Detect_PrezzoMonorario_GAS import PrezzoComponenteGAS 

from ProvePerNomeOfferta import Name
from SplitPDF_EnergiaGas import SplitPDF
from ProveGreen import energiaVerde
from PrezzoF import PrezzoComponenteEnergiaF1, PrezzoComponenteEnergiaF2, PrezzoComponenteEnergiaF3
from ProveCodiceOfferta import CodiceOfferta
from ClassifyDoc import ClassifyDoc

from ConversioneNumeri import replaceNumber


#os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI")
from ProveLetturaTabella import StimaSpesaAnnua
from ProveLetturaTabella_FascePrezzo import StimaSpesaFasce


'''
directory = directory1 
filename = "Agsm_luceweb.pdf"
'''
import pandas as pd

DirSplitted = "D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Pdf_Splitted"


'''
directory1="D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte"
directory2="D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Generalizzazione"

directory = "D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte"
filename = "Sinergy_ValidaFinoNov.pdf"
'''


def ElabFile(directory, filename):
    Prezzo = ""
    ResAll = []

    ResAll = pd.DataFrame(ResAll)
    
    #try:
    a = 1
    if a == 1:
        
        Res = []
        Res = pd.DataFrame(Res)
        
        try:  #in un caso la lettura della convert_pdf_to_txt va in errore -> in except metto lettura con struttura
            Read = read_pdf(os.path.join(directory, filename))
        except:
            Read = read_pdf_2(os.path.join(directory, filename))
            
        Commodity = Read[0]
        Energia = Read[1]
        Gas = Read[2] 
        
        
        #carico cmq tutto il documento con la struttura anche per usarlo in alternativa 
        try:
            Read2 = read_pdf_2(os.path.join(directory, filename))
            
            Energia2 = Read2[1]
            Gas2 = Read2[2] 
        except:
            Energia2 = Energia
            Gas2 = Gas 
        
        #ci sono alcuni casi in cui nella lettura del pdf dopo un trattino si crea uno spazio. Elimino 
        Energia = Energia.replace("- ", "-")
        Gas = Gas.replace("- ", "-")  
        
        #alcuni operatori i costi fissi li scrivono in lettere..
        Energia = replaceNumber(Energia)
        Gas = replaceNumber(Gas)

        
        #carico cmq tutto il documento anche con prima lettura del pdf che avevo usato (senza struttura)
        try:
            Doc1 = convert_pdf_to_txt(os.path.join(directory, filename))
            Doc1 = Doc1.upper()
            Doc1 = replaceNumber(Doc1)
        except:
            pass 


                
        for Com in Commodity['Class']:
            Res = []
            Res = pd.DataFrame(Res)

            if Com == "Energia":
                Doc = Energia
                try:
                    Doc2 = Energia2
                except:
                    Doc2 = Energia
            if Com == "Gas":
                Doc = Gas
                try:
                    Doc2 = Gas2
                except: 
                    Doc2 = Gas

                    
            Res.at[0,'Commodity'] = Com   
                
            try: 
                N = Name(directory, filename)
                Res.at[0,'Name'] = N.iloc[0]
            except:
                pass
            
            
            
            
            #il codice sembra funzionare meglio leggendolo nella versione con struttura 
            Res['CodiceOfferta'] = ""
            try:
                Cod = CodiceOfferta(Doc)
                Res.at[0, 'CodiceOfferta'] = Cod.iloc[0]
            except:
                pass
            #in alcuni casi il codice non viene letto, uso documento letto in altro modo 
            if len(Res['CodiceOfferta']) > 0:
                if Res['CodiceOfferta'][0] == "":
                    try:
                        Cod = CodiceOfferta(Doc)
                        Res.at[0, 'CodiceOfferta'] = Cod.iloc[0]
                    except: 
                        pass
                    
            elif len(Res['CodiceOfferta']) == 0: 
                print('aa') #nel caso in cui il dataframe non ha obs      
                try:
                    Cod = CodiceOfferta(Doc)
                    Res.at[0, 'CodiceOfferta'] = Cod.iloc[0]
                except:
                    pass             






            try:
                if Com == 'Energia':
                    SpA = StimaSpesaAnnua(directory, filename, "2.700")
                    Res.at[0,'StimaSpesaAnnua'] = SpA.iloc[0]
                    #Res['StimaSpesaAnnua'] = SpA 
                elif Com == 'Gas':
                    SpA = StimaSpesaAnnua(directory, filename, "1.400")
                    Res.at[0,'StimaSpesaAnnua'] = SpA.iloc[0]
                    #Res['StimaSpesaAnnua'] = SpA 
                
            except:
                pass
            
            ###########################
            # SE NON TROVO IN TABELLA DA INSERIRE CHECK CON LA SOLITA FUNZIONA SUI 2.700 E PRENDI NUMERO PIù VICINo!
            ###########################
            
            
            #CREO LA COLONNA COME STRINGA
            Res['Price'] = "" 
            
            
            if Com == "Energia":
                #per il prezzo monorario provo prima con approccio in tabelle 
                #se va in errore, applico altra fuznione 
                #F0 lo assegno al Prezzo unico
                try:
                    PF0 = StimaSpesaFasce(directory, filename, "F0")            
                    Res.at[0,'Price'] = PF0.iloc[0]
           
                except:
                    pass
                
                
                Res.Price = Res.Price.fillna('')                
                if Res['Price'][0] == "" or Res['Price'][0] == []:
                    print('aa')
                    try:
                        #Prezzo = PrezzoComponenteEnergia(os.path.join(directory, filename))
                        P = PrezzoComponenteEnergia(Doc)
                        P1 = P[0]
                        P2 = P[1]                    
                        
                        Res.at[0,'Price'] = P1.iloc[0]
                        Res.at[0,'TipoPrezzo'] = P2.iloc[0]
                        #Res['Price'] = P1
                        #Res['TipoPrezzo'] = P2
                    except:
                        pass
                    
                ### F1 ####    
                Res['F1'] = ""
                try:
                    PF1 = StimaSpesaFasce(directory, filename, "F1")
                    Res.at[0,'F1'] = PF1.iloc[0]
                
                except:
                    pass 
                
                Res.F1 = Res.F1.fillna('')                
                if Res['F1'][0] == "" or Res['F1'][0] == []:
                    print('aa')
                    try:
                        PF1 = PrezzoComponenteEnergiaF1(Doc)
                        Res.at[0,'F1'] = PF1.iloc[0]
                    except:
                        pass                
                    
                ### f2 ####
                Res['F2'] = ""
                try:
                    PF2 = StimaSpesaFasce(directory, filename, "F2")
                    Res.at[0,'F2'] = PF2.iloc[0]
                except:
                    pass

                Res.F2 = Res.F2.fillna('')                
                if Res['F2'][0] == "" or Res['F2'][0] == []:
                    try:
                        PF2 = PrezzoComponenteEnergiaF2(Doc)
                        Res.at[0,'F2'] = PF2.iloc[0]
                    except:
                        pass

                ### F3 ###
                Res['F3'] = ""
                try:
                    PF3 = StimaSpesaFasce(directory, filename, "F3")
                    Res.at[0,'F3'] = PF3.iloc[0]
                except:
                    pass
                Res.F3 = Res.F3.fillna('')                
                if Res['F3'][0] == "" or Res['F3'][0] == []:                
                    try:
                        PF3 = PrezzoComponenteEnergiaF3(Doc)
                        Res.at[0,'F3'] = PF3.iloc[0]
                    except:
                        pass


            if Com == "Gas":
                try:
                    P = PrezzoComponenteGAS(Doc)
                    P1 = P[0]
                    P2 = P[1]                    
                        
                    Res.at[0,'Price'] = P1.iloc[0]
                    Res.at[0,'TipoPrezzo'] = P2.iloc[0]
                    #Res['Price'] = P1
                    #Res['TipoPrezzo'] = P2
                except:
                    pass
                
            #se non ho tovato prezzo, provo con seconda conversione dal pdf (in Engie ad esempio
            #la conversione "standard" fa saltare l'ordine) 
                Res.Price = Res.Price.fillna('')                
            
                if len(Res['Price']) > 0:             #nel caso in cui il dataframe ha obs 
                    if Res['Price'][0] == "" or Res['Price'][0] == []:
                        print('aa')
    
                        Gas1 = convert_pdf_to_txt(os.path.join(directory, filename))
                        Gas1 = Gas1.upper()
                        try:
                            P = PrezzoComponenteGAS(Gas1)
                            P1 = P[0]
                            P2 = P[1]                    
                                
                            Res.at[0,'Price'] = P1.iloc[0]
                            Res.at[0,'TipoPrezzo'] = P2.iloc[0]
                            #Res['Price'] = P1
                        except:
                            pass
                
                if len(Res['Price']) == 0:           #nel caso in cui il dataframe non ha obs      
                    print('aa')
                    Gas1 = convert_pdf_to_txt(os.path.join(directory, filename))
                    Gas1 = Gas1.upper()
                    try:
                        P = PrezzoComponenteGAS(Gas1)
                        P1 = P[0]
                        P2 = P[1]                    
                                
                        Res.at[0,'Price'] = P1.iloc[0]
                        Res.at[0,'TipoPrezzo'] = P2.iloc[0]
                        #Res['Price'] = P1
                    except:
                        pass

                
        
            try:
                CV = PrezzoComponenteCommVendita(Doc)                
                Res.at[0, 'PrezzoCV'] = CV.iloc[0]
                #Res['PrezzoCV'] = CV.iloc[0]
            except:
                pass 
            
            
            try:
                DI = PrezzoComponenteDispacciamento(Doc)
                Res.at[0, 'PrezzoDISP'] = DI.iloc[0]
                #Res['PrezzoDISP'] = DI.iloc[0]
            except:
                pass
                          
            try:
                Scad = Scadenza(Doc)
                Res.at[0, 'Scadenza'] = Scad.iloc[0]
                #Res['Scadenza'] = Scad #Scad.iloc[0]
            except:
                pass 
                
                
            try:
                Dur = Durata(Doc)
                Res.at[0, 'Durata'] = Dur.iloc[0]
                #Res['Durata'] = Dur.iloc[0]
            except:
                pass 
                
                
            try:
                E = energiaVerde(Doc)
                E1 = E[0]
                E2 = E[1]
                Res.at[0,'FlagVerde'] = E1.iloc[0]
                Res.at[0,'PrezzoVerde'] = E2.iloc[0]
                
            except:
                pass
                    
            Res['File'] = filename
            Res['Dir'] = directory
            
            ResAll = ResAll.append(Res)
                
             
    '''
    except:
        Res['File'] = filename
        Res['Dir'] = directory
        #pass
    '''

    return ResAll


def Cicla(directory):
    
    import os
    
    Tab = pd.DataFrame(columns = ['File', 'Commodity', 'Name', 'CodiceOfferta', 'StimaSpesaAnnua','Price', 'Dir', 'TipoPrezzo','F1', 'F2', 'F3', 'PrezzoCV', 'PrezzoDISP', 'FlagVerde', 'PrezzoVerde', 'Scadenza', 'Durata'])

    for filename in os.listdir(directory):
        if filename.endswith(".pdf"): 
            print(filename)
            
            Res = ElabFile(directory, filename)
            Tab = Tab.append(Res) 
                
        else:
            continue
    return Tab



