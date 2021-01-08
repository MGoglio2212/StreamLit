# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 16:37:15 2020

@author: gogliom
"""
from PyPDF2 import PdfFileWriter, PdfFileReader



'''
os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte")
'''
'''
DirSplitted = "D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte\Pdf_Splitted"
filename = "E.ON_Luce_Insieme_Web30.pdf"
xxx = SplitPDF(os.path.join(directory1, filename), DirSplitted)        
'''
      
import os
import re
import pandas as pd
import numpy as np
from shutil import copyfile


def SplitPDF(pdf_document, OutDirSplitted):
    Pages = pd.DataFrame(columns = ['Page', 'EnergiaTot', 'GasTot'])
    with open(pdf_document, "rb") as filehandle:

        NomeFile = os.path.basename(pdf_document)
    
        pdf = PdfFileReader(filehandle)
        info = pdf.getDocumentInfo()
        pages = pdf.getNumPages()
    
        for ppp in range(0, pages):
            PPP = pd.DataFrame()
            page = pdf.getPage(ppp)
            Text_ppp = page.extractText()
            Text_ppp = Text_ppp.upper()
            
            word = "ENERGIA"
            Count_Energia = 0
            Count_Energia = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Text_ppp))
    
    
            word = "LUCE"
            Count_Luce = 0
            Count_Luce = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Text_ppp))
    
            word = "KW"
            Count_Kw = 0
            Count_Kw = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Text_ppp))
    
            word = "GAS"
            Count_Gas = 0
            Count_Gas = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Text_ppp))
            
            word = "SMC"
            Count_Smc = 0
            Count_Smc = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), Text_ppp))
    
            Energia_Tot = Count_Energia + Count_Kw + Count_Luce
            Gas_Tot = Count_Gas + Count_Smc
             
            Dict = {
                  "Page": ppp,
                  "EnergiaTot": Energia_Tot,
                  "GasTot": Gas_Tot
                }
                    
            Pages = Pages.append(Dict, ignore_index = True)
    
    filehandle.close()
    
    Pages['Commodity'] = np.where(Pages['EnergiaTot'] > Pages['GasTot'] * 1.5, 'Energia',
                                          np.where(Pages['GasTot'] > Pages['EnergiaTot'] * 1.5, 'Gas','Unknown'))
            
    Pages = Pages[Pages['Commodity'] != 'Unknown']
    NCommodity = set(Pages['Commodity'])
    
    if len(NCommodity) <= 1:
         copyfile(pdf_document, os.path.join(OutDirSplitted, NomeFile))
    elif len(NCommodity) > 1 :
        Energia = Pages[Pages['Commodity'] == "Energia"]   
        Gas = Pages[Pages['Commodity'] == "Gas"]   
            
        inputpdf = PdfFileReader(open(pdf_document, "rb"))
        pdfWriter = PdfFileWriter()
        for ii in Energia['Page']:
            pdfWriter.addPage(inputpdf.getPage(ii))
        with open(os.path.join(OutDirSplitted, '{0}_subset_Energia.pdf'.format(os.path.splitext(NomeFile)[0])), 'wb') as f:
            pdfWriter.write(f)
            f.close()
    
        pdfWriter = PdfFileWriter()          
        for ii in Gas['Page']:
            pdfWriter.addPage(inputpdf.getPage(ii))
        with open(os.path.join(OutDirSplitted, '{0}_subset_Gas.pdf'.format(os.path.splitext(NomeFile)[0])), 'wb') as f:
            pdfWriter.write(f)
            f.close()
    
    return NCommodity

