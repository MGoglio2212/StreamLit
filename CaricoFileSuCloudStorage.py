# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 19:59:07 2020

@author: gogliom
"""


from google.cloud import storage
import os

def upload_to_bucket(blob_name, path_to_file, bucket_name, cred_key):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        cred_key)

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    #returns a public url
    return blob.public_url


#lancio loop per caricare tutti pdf in GCP 

directory1="D:\Altro\RPA\Energy\IREN\TEST CTE\CTE\esempi cte"

for filename in os.listdir(directory1):
    if filename.endswith(".pdf"): 
        ppp = upload_to_bucket(filename
                      ,os.path.join(directory1, filename)
                      ,'pdf_cte'
                      ,'D:\Altro\RPA\Energy\IREN\TEST CTE\DocumentAI\ExtractPDF-8a6a8a0b366c.json')
        


