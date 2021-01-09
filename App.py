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

from operator import itemgetter
import fitz
import pandas as pd
import re


def fonts(doc, granularity=False):
    """Extracts fonts and their usage in PDF documents.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param granularity: also use 'font', 'flags' and 'color' to discriminate text
    :type granularity: bool
    :rtype: [(font_size, count), (font_size, count}], dict
    :return: most used fonts sorted by count, font style information
    """
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles



def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: texts with pre-prended element tags
    """
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s

                    # new block started, indicating with a pipe
                    block_string += "|"

                header_para.append(block_string)

    return header_para



def font_tags(font_counts, styles):
    """Returns dictionary with font sizes as keys and tags as value.
    :param font_counts: (font_size, count) for all fonts occuring in document
    :type font_counts: list
    :param styles: all styles found in the document
    :type styles: dict
    :rtype: dict
    :return: all element tags based on font-sizes
    """
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def main_Pdf_WithStructure(file):

    Doc = fitz.open(stream=file.read(), filetype="pdf")


    font_counts, styles = fonts(Doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(Doc, size_tag)

    return elements 

from google.cloud import storage  
import os

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



'''
with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
'''    
image = Image.open('MicrosoftTeams-image.png')
st.sidebar.image(image, width=225)



st.sidebar.subheader("Seleziona la commodity")
add_selectbox = st.sidebar.selectbox('',
    ('Energia', 'Gas'))

st.sidebar.subheader("Carica un file")
uploaded_file = st.sidebar.file_uploader("", type = "pdf")

st.markdown("<h1 style='text-align: center; color: black;'>CTE Extractor</h1>", unsafe_allow_html=True)

import fitz
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
    
    '''
   Cred = {
  "type": "service_account",
  "project_id": "extractpdf-298515",
  "private_key_id": "8a6a8a0b366cf58e981e2aec543aa871457295ff",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxRWdU5rVap4z1\nOJOA/AmRBqm/rLLg+/kpgFCWNBcgYprri08h0omYeR2OY8aL1HbEwBS/8ZX34+hC\nFMXL/YnjOWDc6/kPW52HJKGka1aq2h1QBOz6/WInyuWAC3/n//+dOnRZHdMJcVgu\nGpVIE99JMTt7cCQ9keJ0iq269BAjjtDa+GEy07UYjPhTCgSoYCkN3tFAXdYYNWZM\nLUaapdPMTErlyq54/PaU6bxDiYPFDOMQL2OGb6Y/PpCD0r2AiRMe/P1YooQRQkBV\nRn4yB5OfJTFlH58NQMgZ5YLJSMUFz06a6fGxW1q3n3iCbwqXMPkNRscV10HvDLnb\nM/g8v8ptAgMBAAECggEADJEzxeOphDDVeqClPl3qd17+TjxvSFQSAinwAfH/7g0S\nLV7TKuiVgMXHUraf7FOmjC9k2TBb4MwbWqyafX9u1M5sH5qqrbbMPbjbAmsUpL3x\nRDYRLyr4QtjCDo2M0V+cmWLRPZcdGgcwc0Dxsn+BfcYb0NYD+l8bANxAUZJnXtSC\nVDXChN4655gqe+2+b9tKNb6rS1yGFePrc720FK4+0JQYkbcnS/+CdHdyAo2zmLws\nJG3Z31NKmzL/LESqOqBF5AmMM99gMUG++MsjMLn+WvFaBBB69ppgkua1w8h0Agfh\nDr5U6grREbfPLGqkYeV8uJeP/ger7IGl4HgLzdrx0QKBgQDrXpvbKIJo8dOHMAWY\n8pOa/b+Y6gS3M1Lnk/gGhWxtEWv7hlWx4E0VDu6SLJXJ8WDUxfFm21fyiOAltyva\nzm13cvBYqG+Rg/b4t3PSvW/FJEwj4410D/G/nYL/JPGsYbQIdaK9vTQYQfDSBtlP\nb0xG0QyWH9VBy5pzpJexvtBQHQKBgQDAzyPToMl5aqLUA2/Yj0H7x39V5/JTNjsN\n43UpnhtzM5ZVoxuTqeALsdZQGFYVz5bLPcRT2slac1tTKR5xoewL6ZJ2vTd50yHg\ns3LEzxucYQNKENvzO5JPVX3NeNOdpQIVca9qjkYxNPNoVMI0Ei+8dzuwJmisTrk+\nwSxbQHPykQKBgQDTY8k+8AcQEgEU7YBZeaQwE648vBE4KJRRAIhF8xcKbhc5c9EL\nTJRuUVbbWce981gwQQcqhd1bKquFtBljDvspyMUsGzr4yjjJ8JnJr/HucUchBIJK\ntvc8TU8VsCyN0cJLxrs/Ber/zllniFcsDJ3JDH/tZPG3ghFZw32qWeHl0QKBgDq5\nnIbjrRnPEeMTXOiP0aAXRkBrEhKoLNpxEgln/6JZ7wsMT+Ts07GcK9NfZjDkdmBW\n4spLlBJ5mjI9Dum7UMLcFGEYBqKTXPksjuNE1XsOzUqs0eFGnqyNNHD1wTZ9wKG5\na50/0j9AinaXgkML2wBDLKndOPpqS9/CRHlSqz4RAoGAQ2J8Kl/VJCT4I/AWkdDS\nz4LnxwRmmY6iqxfPGxzQ8dKrm/oxlY0pXqDE8wxG+CyKikxA3RxB87wLsCFPjIG6\nxkBFVYdw2frka9aXButyxnZHZJT90WfO7uSpuw8Ipk70I6kMLndKVfINZpUfADcr\nkTA4UA2vBalHF4WMqRDSR2M=\n-----END PRIVATE KEY-----\n",
  "client_email": "extractpdf@extractpdf-298515.iam.gserviceaccount.com",
  "client_id": "111857927506471507754",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/extractpdf%40extractpdf-298515.iam.gserviceaccount.com"
}
    '''

    storage_client = storage.Client.from_service_account_json(
    "8a6a8a0b366cf58e981e2aec543aa871457295ff")


    #storage_client = storage.Client.from_service_account_json(
    #r"D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\ExtractPDF-8a6a8a0b366c.json")

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket('pdf_cte')
    blob = bucket.blob('uuu2')
    
    Doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    doc2 = fitz.open()                 # new empty PDF
    doc2.insertPDF(Doc, to_page = 9)  # first 10 pages
    doc2.save(filename="aaaa.pdf")
    st.write(doc2)
    #blob.upload_from_file(doc2)
    blob.upload_from_filename("aaaa.pdf")
    
    '''
    st.write(Doc)
    font_counts, styles = fonts(Doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(Doc, size_tag)
    
    st.write(elements)
    '''
    
    '''
    storage_client = storage.Client.from_service_account_json(
    'D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\ExtractPDF-8a6a8a0b366c.json')

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket('pdf_cte')
    blob = bucket.blob('uuu')
    
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    #device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(uploaded_file, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    
    
    st.write(text)
    '''
    '''
    with NamedTemporaryFile(mode='wb') as temp:
        temp.write(base64.b64decode(uploaded_file))
        
    blob.upload_from_file(temp)
    '''
    
    '''
        pdfReader = PdfFileReader(uploaded_file)
        pdf_writer = PdfFileWriter()
        count = pdfReader.numPages
        all_page_text = ""
        
        tmp = StringIO()
        for i in range(count):
            page = pdfReader.getPage(i)
            #all_page_text += page.extractText()   
            pdf_writer.addPage(page)
        
        pdf_writer.write(tmp.getvalue())
        #base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
    
        #pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">' 
        #st.markdown(pdf_display, unsafe_allow_html=True)
        
        

        
        
        ppp = upload_to_bucket("xxx"
                      ,tmp
                      ,'pdf_cte'
                      ,'D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\ExtractPDF-8a6a8a0b366c.json')
    '''
    
    '''
    #la lettura del file può avvenire una volta sola
    #quindi dalla read pdf mi porto fuori anche il pdf con struttura che servità ad es per la name
    try:  #in un caso la lettura della convert_pdf_to_txt va in errore -> in except metto lettura con struttura
            Read = read_pdf(uploaded_file)
    except:
            Read = read_pdf_2(uploaded_file)
            
    Commodity = Read[0]
    Energia = Read[1]
    Gas = Read[2] 
    PdfSt = Read[3]
        
    
        #carico cmq tutto il documento con la struttura anche per usarlo in alternativa 
    try:
            Read2 = read_pdf_2(uploaded_file)
            
            Energia2 = Read2[1]
            Gas2 = Read2[2] 
    except:
            Energia2 = Energia
            Gas2 = Gas 
            
            
    Res = ElabFile(Commodity, Energia, Energia2, Gas, Gas2, PdfSt)

        
    st.write(Res)
    '''

    
    
