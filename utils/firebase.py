"""
This module will contain helper functions that pertain to using Firebase Storage.
The developer must create an json file with the format stated in the README.md
which contains the credientials of the DB.
"""

import firebase_admin
from firebase_admin import credentials, storage
from utils.database import add_note_to_db
from urllib.parse import quote
import uuid


# setting up connection to firebase DB using credentials
# gives access to SDK
cred = credentials.Certificate("rattler-notehub-firebase.json")
firebase_admin.initialize_app(cred, {
    'storageBucket' : 'rattler-notehub.appspot.com' #reference to the default storage bucket
})
bucket = storage.bucket()

# sending the file to firebase Storage
def upload_to_firebase(file):
    
    #unique id to distinguish multiple files with same name
    unique_id = str(uuid.uuid4())

    # upload the file to Firebase Storage
    file_name = f"{file.split('/')[-1]}_{unique_id}"  # add unique ID to the filename
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file)

    
    file_path = blob.name # must use unique ID + filename
    encoded_file_path = quote(file_path, safe='') # adding % symbol into each space

    bucket_name = "rattler-notehub.appspot.com"
    url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_file_path}?alt=media" # file path format to publicly access all files

    add_note_to_db(url)

    return url

# permanently deleting file from Firebase
def delete_file_from_firebase(url):
    # extract the encoded_file_path   
    start_index = url.find("/o/") + len("/o/")
    end_index = url.find("?alt=media")
    encoded_file_path = url[start_index:end_index]
    
    # file needs to be the name of the file
    # Get the Blob object for the file to delete
    blob = bucket.blob(encoded_file_path)

    # delete file
    blob.delete()

"""
# testing
if __name__ == '__main__': 

    file_path = "/Users/emilym/Downloads/haiku.pdf"
    uploaded_url = upload_to_firebase(file_path)
    print("File uploaded successfully. URL:", uploaded_url)

    
    url = "https://firebasestorage.googleapis.com/v0/b/rattler-notehub.appspot.com/o/haiku.pdf_b44a4928-c6ce-4792-ba86-de6f7b868c88?alt=media"
    
    # extract the encoded_file_path
    start_index = url.find("/o/") + len("/o/")
    end_index = url.find("?alt=media")
    encoded_file_path = url[start_index:end_index]

    print("Encoded File Path:", encoded_file_path)

"""
