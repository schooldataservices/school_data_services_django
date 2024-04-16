

#SFTP 

# # Use
# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None


# #Get Data from PS Data Export Manager SFTP folder, and move to BigQuery
# with pysftp.Connection(
#     host="ps.com",
#     username="greendot",
#     password="*********",
#     cnopts=cnopts
# ) as sftp:
#     # Download a remote file to the local machine
#     remote_file = "/greendottn/custom_report_standards_2024"
#     local_file = "local_file.csv"   (This can be dynamic if we want to preserve the file everytime)
#     sftp.get(remote_file, local_file)

# ----------------------------------------------------------

from modules.buckets import create_bucket, upload_to_bucket, download_from_bucket
import os

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable in order to interact
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'greendotdataflow-848329b50f47.json'

#Create the bucket, and upload to that bucket. If already created, bypass
create_bucket('psholdingbucket6')

#Upload file to bucket, demonstrates if overwritten or newfile. 
#End File Name,  Local File Path, Bucket Name

upload_to_bucket('students.csv' , 'Student_Records.csv', 'psholdingbucket6' )









# if upload_status == 'Error': 
#     print('File not uploaded, download did not occur')
# else:
#     download_from_bucket('students.csv', 'students_download.csv', 'psholdingbucket5')


        
