import os
import time
import random
import json
from google.cloud import storage, bigquery  # , pubsub_v1
from google.oauth2 import service_account
from io import BytesIO
import requests
from PIL import Image, ImageDraw

project_id = 'xtreamly-ai'
dataset_id = 'xtreamly_raw'
auth_file = os.path.join('settings', f'xtreamly-ai-cc418ba37b0c.json')
credentials = None
if os.path.isfile(auth_file):
    credentials = service_account.Credentials.from_service_account_file(
        auth_file)
else: print('no credentials')

client_storage = storage.Client(credentials=credentials, project=project_id)
client_bigquery = bigquery.Client(credentials=credentials, project=project_id)

client_st = storage.Client(credentials=credentials, project=project_id)
client_bq = bigquery.Client(credentials=credentials, project=project_id)

def _upload_blob_json(content, name_bucket, loc):
    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(loc)
    blob.upload_from_string(data=json.dumps(content), content_type='application/json')

def _upload_blob_pdf(pdf, name_bucket, blob_name):
    byte_string = pdf.output(dest="S")
    stream = BytesIO(byte_string)
    stream.seek(0)
    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(stream, content_type='application/pdf')

def _upload_blob_img(image_url, name_bucket, blob_name):
    response = requests.get(image_url)
    image_content = response.content
    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data=image_content, content_type='image/png')

def _read_blob_json(name_bucket, loc):
    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(loc)
    file_content = blob.download_as_string()
    json_content = json.loads(file_content)
    return json_content

def _read_blob_img(name_bucket, blob_name):
    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(blob_name)
    image_data = blob.download_as_bytes()
    image = Image.open(BytesIO(image_data))
    return image

def _delete_blob(name_bucket, blob_name):

    bucket = client_storage.bucket(name_bucket)
    blob = bucket.blob(blob_name)
    generation_match_precondition = None

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)