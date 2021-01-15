# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 15:28:47 2021

@author: gogliom
"""
import os
#os.chdir("D:\Altro\RPA\Energy\IREN\TEST CTE\App\StreamLit")

import streamlit as st
from PIL import Image
from ElabFile import ElabFile 
from Read_Pdf import read_pdf  #importazione basata sul pacchetto che tiene struttura
from LetturaPdf_2 import read_pdf_2 #importaizone basata sulla convert_pdf_to_txt e poi splittata in ele / gas in base ai paragrafi
from ProvePerNomeOfferta import Name
import base64
from Loop import ElabFile

from ChiamataSincrona import parse_table
from operator import itemgetter
import fitz
import pandas as pd
import re
from google.cloud import storage  
import os
import json 

from google.oauth2 import service_account


def decryptHard(message):
    newS=''
    for i in range(len(message)):
        if i%2==0:
            newS=newS+chr(ord(message[i])-3)        
        else:
            newS=newS+chr(ord(message[i])+2)        
     
    return newS


with open('MOD.json') as f:
  data = json.load(f)
  data['client_id'] = '106427812775067397180'
  data['private_key_id'] = 'fde5773fdc37fe15f1560192ff4306706397af93'
  data['private_key'] = '-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCvyRwCAL+0ytiO\nVZ+m9ECaCrgvE8RaeYE8hJg2J+2Wx7fzqeE+3COXNE/BpwzMuY39dEil8eiXnwOe\n/b9fYfIurTmyIh5qJbpkXNA6haecOg+JPi5jYtQF9tbRDKMXqeWvSlBN6cz0VHXR\nQMtbP3nvJVc8sjsd40+OY7xAT1B8mFmfRCy51fpJT/q6s9eK94qFK5XGiAAIprBq\nU6OES3WhCoOR73P9FIYkmpPVbCsnUmFdlnCf/i3RioCL+SrXsgXecP9jZ2xKsRtk\nRUgtZcAmKQPsHvvf1uYanhrrzjARbbcpyZwEti/fWxP3e3URTBMF1Kgi9hYRASYO\nMYWvyi4BAgMBAAECggEAAOjcYF3G4C1/CKCEjJl9tpZY3OSAKvwvOSQSAhC7k+DJ\ncMU3pUrAE+WZRo4h3LLWm2HFSPeLHbK80u8q9PhFp6xtjKCM0f2LPP72dGER7Jbn\n0uzbklfV80hzVN5Y/zO5vKoYp4iOzxJbUDeCveCCleRWctnUwLs3A4x8UkRezSA9\n+ppXlHMNOa4my9CY5OS5WEqZhA/w6qAh3kMo2jhLFEA2xXdlpb96ezXevmcGCg9y\nHCZC5qURCdfcP/1yJ3v5hhRxxYNyCyO9eGDnrjjk4z3No1km3PKAmmxHNl8otZ+T\njbv00xPP34b7hI/ZmU9vnB/KS0HN0wAWZg91k59YAQKBgQDx4SKZFg62l3lu+HL4\nMnlaveoknWhaJqeFNuBdNyz5RccToHrQ/r/kcxnHHp75XhIhvTCqjrF9a9FIaFxD\n51XQ2SULhfdjlY8bXZTH+Y3OdYVBCT1fMA5IO4Ul9Euw3r6IeEQI/LH/TChXEkUi\nO5RvXeINdLRBClnU4MzsZNl2gQKBgQC6DDVBIyj7/o0+4WDkQmryJjlgzvKPR8Ze\nVFxydWU4Gb6nw0fS6dqLeG7Pt3Lve1IMaUs4aLOvzhF4as0zPCDxUrJB1qsnsBs3\ntB+1Cu3Y3YFpISENLxVLLHfgMFFGFeCWieIA12l502DAcpHThBG4LmR2+gyNLTgk\nbuRak1/3gQKBgBug+dC+wkN9HfPdEVTkfxQsaVhxWoAhtjTzRcGgEdUPcWP+isjg\nsI6pzyH9j28wnaWY9LwmvIN1E1zP/uoKvLS0eRTN4qpPZR9dGyeUi+wvZF8/bPE4\njgkWM2lYdGTprJ3uDudv5e0hh+IaRidY4uWttaqP0B81zXkRjJbcFjMBAoGAKYgs\nIzxcG9T5Zv4dCReilCfgSzInh8C4Ebq3YH3AeMOWghDf6b92oAfkhM4pBDj9WfPv\nbMpCwo437C+7WyKjH/wb+wKW9qcjjE3TfjDQY8ce6n8Qx8ao9D0bDZr7qa+ckT56\ni0GLNDzxrkRlNViYNAt3NfAf+SwNCmUO6QFZPQECgYAo1KMLhRpvSnzBQri0OmJ/\newYNyPlv/SAJ8e6FD/I6QhUYWtuECkruT15KKZYhSJfZaw0/izLv73IurzsRBR6E\nl/tpe5CS+LeOR0/c0ZQQhA9sk5TNDGeL8tRWzJESQJa0ef2qXlsw9SQEpXAXlJym\nZzehyLj/JHWGUWe/r3DW/g==\n-----END PRIVATE KEY-----\n'
  data['client_email'] = "extractpdfv002@extractpdfv002.iam.gserviceaccount.com"
  data['project_id'] = 'extractpdfv002'
  


with open(r'Cred.json', 'w') as outfile:
    json.dump(data, outfile)
    



cred = service_account.Credentials.from_service_account_file("Cred.json")


def upload_to_bucket(blob_name, file, bucket_name, cred_key):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        cred_key)

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    
    blob.upload_from_file(file,content_type = 'application/pdf')

    #returns a public url
    return blob.public_url



image = Image.open('MicrosoftTeams-image.png')
st.sidebar.image(image, width=225)


st.sidebar.subheader("Seleziona la commodity")
add_selectbox = st.sidebar.selectbox('',
    ('Energia', 'Gas'))

st.sidebar.subheader("Carica un file")
uploaded_file = st.sidebar.file_uploader("", type = "pdf")

st.markdown("<h1 style='text-align: center; color: black;'>ESTRATTORE Info da file CTE - SCHEDA CONFRONTABILITA'</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: black;'>Energia Gas</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: black;'>Caricare file pdf e selezionare commodity per cui si vogliono informazioni</h4>", unsafe_allow_html=True)



import fitz
fitz.TOOLS.mupdf_display_errors(False)
from io import StringIO
import base64

from tempfile import NamedTemporaryFile
from PyPDF2 import PdfFileReader, PdfFileWriter

#riesco a scrivere la stringa scommentando all_page_text e modificando l'upload nel bucket sopra con upload_from_string
#anzichè upload_from_file (e togliendo 'application') , ma come stringa non va bene poi per passaggio a api di google

import os
from tempfile import NamedTemporaryFile

import pdfminer
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

if uploaded_file is not None:
    
    filename = uploaded_file.name
    Doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    Doc2 = fitz.open()
    Doc2.insertPDF(Doc, to_page = 9)  # first 10 pages
    Doc2.save(filename=filename)

    #if os.path.isfile('Cred.json'):   #se c'è file con credenziali, faccio giro completo con anche upload su GCP e analisi tabelle con Google API
    
    
    with open(r'Cred.json', 'w') as outfile:
        json.dump(data, outfile)     

    storage_client = storage.Client.from_service_account_json("Cred.json")
    
        #print(buckets = list(storage_client.list_buckets())
    
    bucket = storage_client.get_bucket('pdf_cte_v002')
    
 
        
    blobName = bucket.blob(filename)
    blobs = storage_client.list_blobs('pdf_cte_v002')
        
        
    ListaFileGCP = list()
    for blob in blobs:
        ListaFileGCP.append(blob.name.upper())
            
           
        
        
    #se un pdf non ha tabelle non viene creato il pickle.
    #quindi se ripasso lo stesso file, il pickle non viene trovato e viene fatta richiesta a google 
    #quindi decido di modificare la condizione, filtrando per il fatto se il pdf è già presente sul bucket 
    #se già presente, lo avrò già analizzato
    #altrimenti lo carico e lo analizzo con api google 
    
    #devo scaricare anche il pickle    
    NPICKLE = os.path.splitext(filename)[0]
    NPICKLE = NPICKLE + '.pkl'
    blobName_PICKLE = bucket.blob(NPICKLE)
    
    if filename.upper() in ListaFileGCP:
        pass  
    else:
            
        #blob.upload_from_file(doc2)
        blobName.upload_from_filename(filename)
            

    
        PC = 'gs://pdf_cte_v002/'+filename
            
            
        xxx = parse_table(project_id='extractpdfv002',
                    input_uri = PC ,
                    filename = filename,
                    cred = cred)
        xxx.to_pickle(os.path.join(NPICKLE), protocol = 2)
        blobName_PICKLE.upload_from_filename(NPICKLE)
    
        #Scarico file pdf da gcp a questo punto
    blobName.download_to_filename(filename)
    blobName_PICKLE.download_to_filename(NPICKLE)
    Result = ElabFile("", filename, NPICKLE)


    
    #elif not os.path.isfile('Cred.json'): #non ho caricato file di credenziali, quindi faccio lettura diretta del file pdf senza passare da google (e non mostro stimaspesaanua)
        #Result = ElabFile("", filename , "")
    


    Result = Result[Result['Commodity'] == add_selectbox]
    
    if len(Result) == 0:
        st.write("Nel file non ci sono informazioni per la commodity selezionata")
    else: 
        
        Colonne = Result.columns 
        
        #se un pdf non ha tabelle non viene creato il pickl    
        ColonneToBe = ['Commodity', 'Name', 'CodiceOfferta', 'StimaSpesaAnnua', 'Price', 'F1',
           'F2', 'F3', 'TipoPrezzo', 'PrezzoCV', 'PrezzoDISP', 'Scadenza',
           'Durata', 'FlagVerde', 'PrezzoVerde', 'File', 'Dir']
    
        for col in ColonneToBe:
            if col in Colonne:
                pass
            else:
                Result[col] = ""
                
        
        NomeOfferta = str(Result['Name'].iloc[0])
        CodiceOfferta = str(Result['CodiceOfferta'].iloc[0])
        StimaSpesaAnnua = str(Result['StimaSpesaAnnua'].iloc[0])
        Price = str(Result['Price'].iloc[0])
        F1 = str(Result['F1'].iloc[0])
        F2 = str(Result['F2'].iloc[0])
        F3 = str(Result['F3'].iloc[0])
        TipoPrezzo = str(Result['TipoPrezzo'].iloc[0])
        PrezzoCV = str(Result['PrezzoCV'].iloc[0])
        Scadenza = str(Result['Scadenza'].iloc[0])
        Durata = str(Result['Durata'].iloc[0])
        FlagVerde = str(Result['FlagVerde'].iloc[0])
        PrezzoVerde = str(Result['PrezzoVerde'].iloc[0])
        CodiceOfferta = str(Result['CodiceOfferta'].iloc[0])
        Commodity = str(Result['Commodity'].iloc[0])
        
        
    
        st.markdown("<h3 style='text-align: left; color: black;'>Nome Offerta:</h1>", unsafe_allow_html=True)
        st.write(NomeOfferta.upper())
        
        #if os.path.isfile('Cred.json'):        
        st.markdown("<h3 style='text-align: left; color: black;'>Stima spesa annua:</h1>", unsafe_allow_html=True)
        st.write(StimaSpesaAnnua.upper())
        
        st.markdown("<h3 style='text-align: left; color: black;'>Prezzo unitario materia prima:</h1>", unsafe_allow_html=True)
        st.write(Price.upper())
    
        if Commodity == 'Energia':
            st.markdown("<h3 style='text-align: left; color: black;'>Prezzo unitario F1:</h1>", unsafe_allow_html=True)
            st.write(F1.upper())
            st.markdown("<h3 style='text-align: left; color: black;'>Prezzo unitario F2:</h1>", unsafe_allow_html=True)
            st.write(F2.upper())
            st.markdown("<h3 style='text-align: left; color: black;'>Prezzo unitario F3:</h1>", unsafe_allow_html=True)
            st.write(F3.upper())
        
        
        st.markdown("<h3 style='text-align: left; color: black;'>Tipo Prezzo:</h1>", unsafe_allow_html=True)
        st.write(TipoPrezzo.upper())
        
        st.markdown("<h3 style='text-align: left; color: black;'>Quota Commercializzazione Vendita:</h1>", unsafe_allow_html=True)
        st.write(PrezzoCV.upper())
    
        st.markdown("<h3 style='text-align: left; color: black;'>Scadenza:</h1>", unsafe_allow_html=True)
        st.write(Scadenza.upper())
    
        st.markdown("<h3 style='text-align: left; color: black;'>Durata:</h1>", unsafe_allow_html=True)
        st.write(Durata.upper())
    
        if Commodity == 'Energia':
            st.markdown("<h3 style='text-align: left; color: black;'>Energia Verde Y/N:</h1>", unsafe_allow_html=True)
            st.write(FlagVerde.upper())
    
            st.markdown("<h3 style='text-align: left; color: black;'>Eventuale Prezzo opzione verde:</h1>", unsafe_allow_html=True)
            st.write(PrezzoVerde.upper())
        
        #st.markdown("<h3 style='text-align: left; color: black;'>Codice Offerta:</h1>", unsafe_allow_html=True)
        #st.write(CodiceOfferta.upper())
    
