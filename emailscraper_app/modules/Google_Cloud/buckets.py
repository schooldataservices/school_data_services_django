import os
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.cloud import bigquery
import pandas as pd
import pandas_gbq
import logging
from .reproducibility import *




def create_bucket(bucket_name, location, storage_class = 'STANDARD'):

    storage_client = storage.Client()

    try:
        # Attempt to get the bucket
        bucket = storage_client.get_bucket(bucket_name)
        logging.info(f'Bucket {bucket_name} already exists')
        print(f'\n\nBucket {bucket_name} already exists.')
    
    except NotFound:
        # Bucket not found, create a new one with storage_class arg and location
        bucket = storage_client.bucket(bucket_name)
        bucket.storage_class = storage_class

        print(location)

        bucket = storage_client.create_bucket(bucket, location)
        print(f'\n\nBucket {bucket_name} created in {location} with {storage} storage class.')
        logging.info(f'\n\nBucket {bucket_name} created in {location} with {storage} storage class.')
    


#blob name is the name of the file once uploaded
#file_path is local file path
#bucket name is GC bucket unique bucket name

def upload_to_bucket(destination_blob_name, local_file, bucket_name):

    # Initialize a Google Cloud Storage client
    storage_client = storage.Client()

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Get the existing blob/filename in the bucket (if it exists)
        existing_blob = bucket.get_blob(destination_blob_name)
        existing_updated_time = existing_blob.updated if existing_blob else None

        # Upload the local file
        blob.upload_from_filename(local_file)

        # Check if the file was overwritten based on blob names
        if existing_blob and existing_blob.name == destination_blob_name:
            print(f"File {destination_blob_name} in bucket {bucket_name} was overwritten by local file {local_file}.")
            logging.info(f"File {destination_blob_name} in bucket {bucket_name} was overwritten by local file {local_file}.")
        else:
            print(f"Local File {local_file} was uploaded as a new file {destination_blob_name} in the bucket {bucket_name}.")
            logging.info(f"Local File {local_file} was uploaded as a new file {destination_blob_name} in the bucket {bucket_name}.")

    except Exception as e:
        print(e)
        logging.info(f'Error uploading {local_file} to the {bucket_name} due to {e}')


def upload_all_files_to_bucket(local_dir, bucket_name):
    for filename in os.listdir(local_dir):
        local_file_path = os.path.join(local_dir, filename)
        if os.path.isfile(local_file_path):
            upload_to_bucket(filename, local_file_path, bucket_name)
        else:
            logging.info(f'{local_file_path} is not a file')



def list_files_in_bucket(bucket_name):

    # Initialize a Google Cloud Storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # List all blobs (files) in the bucket
    blobs = bucket.list_blobs()

    # Iterate over each blob and print its name
    file_names = [blob.name for blob in blobs]

    if file_names == []:
        logging.info(f'There are no files in the GCS bucket {bucket_name}')
    
    return(file_names)







#Upload to BiqQuery using Pandas_GBQ. 
#Schema is created based on pandas dtypes. 
        
def upload_to_bq_table(cloud_storage_uri, project_id, db, table_name, location, append_or_replace):

  
    # Read the CSV file from Cloud Storage into a Pandas DataFrame
    try:
        df = read_file(cloud_storage_uri) #here is where the error is occuring 'gs://eisbucket-iotaschools-1/EIS_prior_schools.csv'
        df = pre_processing(df)
        

    except pd.errors.ParserError as e:
        logging.error(f'Unable to read {cloud_storage_uri} due to parsing error: \n {e}')
      

    except pd.errors.EmptyDataError as e:
        logging.error(f'Unable to read {cloud_storage_uri} due to empty data: \n {e}')
        
    except Exception as e:
        logging.error(f'Here is the error after reading in cloud storage uri : \n {e}')


    logging.info(f'Here is the cloud uri that was read {cloud_storage_uri}')

    client = bigquery.Client()

    # project, DB, table name
    table_id = f'{project_id}.{db}.{table_name}'

    try:
        client.get_table(table_id)
        print(f'Table {table_id} already exists, argument is being called to {append_or_replace.upper()} new data with incoming data')
        logging.info(f'Table {table_id} already exists, argument is being called to {append_or_replace.upper()} new data with incoming data')
   
    except NotFound:
        print(f'Attempting to create table {table_id} and send data for the first time')
        logging.info(f'Attempting to create table {table_id} and send data for the first time')

    try:
        pandas_gbq.to_gbq(df, table_id, project_id, if_exists=append_or_replace, location=location)
        logging.info(f'Succesfully created table {table_id} and sent data')
    except Exception as e:
        logging.info(f'Unable to create table {table_id} due to error- {e}')






   
class Create:

    def __init__(self, bucket, local_dir, project_id, db, append_or_replace, location=None):
        
        self.location = location
        self.bucket = bucket
        self.local_dir = local_dir
        self.project_id = project_id
        self.db = db
        self.append_or_replace = append_or_replace


    def process(self):

        logging.info('New file processing started\n')
    
        #Create the bucket, and upload to that bucket. If already created, bypass
        create_bucket(self.bucket, self.location, self.local_dir)
  
        #Upload all files to bucket based on self.local_dir, demonstrates if overwritten or newfile for all files in logging
        upload_all_files_to_bucket(self.local_dir, self.bucket)

        print(self.bucket)

        #Get file_names to upload to BQ as their table name
        file_names = list_files_in_bucket(self.bucket)
        #shows ['EIS_prior_schools.csv'] here
        file_names_without_extension = [remove_extension_from_file(file_name) for file_name in file_names]

        
        

        for file_name, table_name in zip(file_names, file_names_without_extension):
            logging.info(f'Attempting to upload {file_name} into the table {table_name}')
            upload_to_bq_table(
                cloud_storage_uri=f'gs://{self.bucket}/{file_name}',
                project_id=self.project_id,
                db=self.db,
                table_name=table_name,
                location=self.location,
                append_or_replace=self.append_or_replace
            )

# 'EIS_prior_schoolsbucket-iotaschools-1' this is the bucket at some point not sure why under global variables
         
            










def download_from_bucket(source_blob_name, destination_file_path, bucket_name):

    #Initialize a Google Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    if os.path.exists(destination_file_path) == True:
        print(f'Downloading {source_blob_name} file from bucket. Local file being overwritten as: {destination_file_path}')
        logging.info(f'Downloading {source_blob_name} file from bucket. Local file being overwritten as: {destination_file_path}')

    try:
        # Download the blob to a local file
        blob.download_to_filename(destination_file_path)
        print(f'File {source_blob_name} downloaded from bucket as {destination_file_path}')
        logging.info(f'File {source_blob_name} downloaded from bucket as {destination_file_path}')

    except Exception as e:
        print(e)




        # #Could implement sql query here if did not want to be in class instance

        # try:
        #     logging.info(f'Calling SQL query on {self.project_id}.{self.db}.{self.table_name}')
        #     print(f'Calling SQL query on {self.project_id}.{self.db}.{self.table_name}')

        #     query = pandas_gbq.read_gbq(self.sql_query, project_id=self.project_id, location=self.location)

        #     logging.info('SQL Query completed')
        #     print('SQL Query completed')

        # except Exception as e:
        #     print(f'Unable to run query on {self.project_id}.{self.db}.{self.table_name} due to {e}')
        #     logging.info(f'Unable to run query on {self.project_id}.{self.db}.{self.table_name} due to {e}')

        # return(query)re