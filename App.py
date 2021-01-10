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

from google.oauth2 import service_account


if os.path.isfile('ExtractPDF-8a6a8a0b366c.json'):
    cred = service_account.Credentials.from_service_account_file("ExtractPDF-8a6a8a0b366c.json")


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

st.markdown("<h1 style='text-align: center; color: black;'>ESTRATTORE CTE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: black;'>Energia Gas</h2>", unsafe_allow_html=True)


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

    if os.path.isfile('ExtractPDF-8a6a8a0b366c.json'):   #se c'è file con credenziali, faccio giro completo con anche upload su GCP e analisi tabelle con Google API
    
     
        storage_client = storage.Client.from_service_account_json("ExtractPDF-8a6a8a0b366c.json")
    
        #print(buckets = list(storage_client.list_buckets())
    
        bucket = storage_client.get_bucket('pdf_cte')
    
 
        
        blobName = bucket.blob(filename)
        blobs = storage_client.list_blobs('pdf_cte')
        
        
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
            
            '''
            doc2 = fitz.open()                 # new empty PDF
            doc2.insertPDF(Doc, to_page = 9)  # first 10 pages
            doc2.save(filename=filename)
            #blob.upload_from_file(doc2)
            blobName.upload_from_filename(filename)
            '''
    
    
            PC = 'gs://pdf_cte/'+filename
            
            
            xxx = parse_table(project_id='extractpdf-298515',
                    input_uri = PC ,
                    filename = filename,
                    cred = cred)
            xxx.to_pickle(os.path.join(NPICKLE), protocol = 2)
            blobName_PICKLE.upload_from_filename(NPICKLE)
    
        #Scarico file pdf da gcp a questo punto
        blobName.download_to_filename(filename)
        blobName_PICKLE.download_to_filename(NPICKLE)
        Result = ElabFile("", filename, NPICKLE)


    elif not os.path.isfile('ExtractPDF-8a6a8a0b366c.json'): #non ho caricato file di credenziali, quindi faccio lettura diretta del file pdf senza passare da google (e non mostro stimaspesaanua)
        Result = ElabFile("", filename , "")



    Result = Result[Result['Commodity'] == add_selectbox]
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
    
    if os.path.isfile('ExtractPDF-8a6a8a0b366c.json'):        
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
    
    st.markdown("<h3 style='text-align: left; color: black;'>Codice Offerta:</h1>", unsafe_allow_html=True)
    st.write(CodiceOfferta.upper())
    
