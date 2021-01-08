# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 16:41:58 2020

@author: gogliom
"""


#PRIMA DI LANCIARE , DA ENVIRONMENT IN ANACONDA:   
#set GOOGLE_APPLICATION_CREDENTIALS=D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\ExtractPDF-8a6a8a0b366c.json

OutDir = "D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\Output"
import os
from google.cloud import documentai_v1beta2 as documentai

import pandas as pd


def parse_table(project_id
                ,input_uri 
                ,filename ):
    """Parse a form"""
    
    RIGHE = []
    RIGHE = pd.DataFrame(RIGHE)
    
    
    

    client = documentai.DocumentUnderstandingServiceClient()

    gcs_source = documentai.types.GcsSource(uri=input_uri)

    # mime_type can be application/pdf, image/tiff,
    # and image/gif, or application/json
    input_config = documentai.types.InputConfig(
        gcs_source=gcs_source, mime_type='application/pdf')

    # Improve table parsing results by providing bounding boxes
    # specifying where the box appears in the document (optional)
    table_bound_hints = [
        documentai.types.TableBoundHint(
            page_number=1,
            bounding_box=documentai.types.BoundingPoly(
                # Define a polygon around tables to detect
                # Each vertice coordinate must be a number between 0 and 1
                normalized_vertices=[
                    # Top left
                    documentai.types.geometry.NormalizedVertex(
                        x=0,
                        y=0
                    ),
                    # Top right
                    documentai.types.geometry.NormalizedVertex(
                        x=1,
                        y=0
                    ),
                    # Bottom right
                    documentai.types.geometry.NormalizedVertex(
                        x=1,
                        y=1
                    ),
                    # Bottom left
                    documentai.types.geometry.NormalizedVertex(
                        x=0,
                        y=1
                    )
                ]
            )
        )
    ]

    # Setting enabled=True enables form extraction
    table_extraction_params = documentai.types.TableExtractionParams(
        enabled=True, table_bound_hints=table_bound_hints)

    # Location can be 'us' or 'eu'
    parent = 'projects/{}/locations/us'.format(project_id)
    request = documentai.types.ProcessDocumentRequest(
        parent=parent,
        input_config=input_config,
        table_extraction_params=table_extraction_params)

    document = client.process_document(request=request)

    def _get_text(el):
        """Convert text offset indexes into text snippets.
        """
        response = ''
        # If a text segment spans several lines, it will
        # be stored in different text segments.
        for segment in el.text_anchor.text_segments:
            start_index = segment.start_index
            end_index = segment.end_index
            response += document.text[start_index:end_index]
        return response

    for page in document.pages:
        print('Page number: {}'.format(page.page_number))
        for table_num, table in enumerate(page.tables):
            print('Table {}: '.format(table_num))
            for row_num, row in enumerate(table.header_rows):
                cells = '\t'.join(
                    [_get_text(cell.layout) for cell in row.cells])
                print('Header Row {}: {}'.format(row_num, cells))
                
                ppp1 = cells.split('\n')
                ppp1 = pd.DataFrame([x.split('\t') for x in ppp1])
                ppp1['RowNum_Header'] = row_num
                ppp1['Table'] = table_num
                ppp1['Page'] = page.page_number

                RIGHE = RIGHE.append(ppp1)

            for row_num, row in enumerate(table.body_rows):
                cells = '\t'.join(
                    [_get_text(cell.layout) for cell in row.cells])
                print('Row {}: {}'.format(row_num, cells))
                
                
                ###MODIFICHE MARCO PER CERCARE DI METTERE IN DATAFRAME ANZICHE PRINTARE
                
                ppp1 = cells.split('\n')
                ppp1 = pd.DataFrame([x.split('\t') for x in ppp1])
                ppp1['RowNum'] = row_num
                ppp1['Table'] = table_num
                ppp1['Page'] = page.page_number

            
                RIGHE = RIGHE.append(ppp1)
                
                FF = os.path.splitext(filename)[0] 
                FF = FF + '.pkl'
                RIGHE.to_pickle(os.path.join(OutDir, FF))
        
    return RIGHE
            



'''
## lancio ciclo e salvo pickle
import pandas as pd
from google.cloud import storage

storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
blobs = storage_client.list_blobs('pdf_cte')

for blob in blobs:
    NF = blob.name 
    PC = 'gs://pdf_cte/'+NF
    
    NPICKLE = os.path.splitext(NF)[0]
    NPICKLE = NPICKLE + '.pkl'
    Percorso = os.path.join(OutDir, NPICKLE)
        
    print(Percorso)
    
    if os.path.isfile(Percorso) == True:
        print('File già esistente')
    else:
        print('Elaborazione GG')
        xxx = parse_table(project_id='extractpdf-298515',
                input_uri = PC ,
                filename = NF)

        
        
    
#xxx = pd.read_pickle('D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\Output\Acea_Come_Noi_CE_DOM.pkl')




            
xxx = parse_table(project_id='extractpdf-298515',
                input_uri='gs://pdf_cte/Acea_Come_Noi_CE_DOM.pdf')
            
print(xxx)



##RECUPERARE FILE DA GOOGLE STORAGE
from google.cloud import storage
# create storage client
storage_client = storage.Client.from_service_account_json('D:/Altro/RPA/Energy/IREN/TEST CTE/DocumentAI/ExtractPDF-8a6a8a0b366c.json')
# get bucket with name
bucket = storage_client.get_bucket('pdf_cte')
# get bucket data as blob
blob = bucket.get_blob('ENI_SchedaConfrontabilita.pdf')
# convert to string
json_data = blob.download_as_string()
'''