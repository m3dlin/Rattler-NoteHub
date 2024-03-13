import firebase_admin
from firebase_admin import credentials, firestore, storage
from database import add_note_to_db
from datetime import timedelta
from urllib.parse import quote


# setting up connection to firebase DB using credentials
# gives access to SDK
cred = credentials.Certificate("rattler-notehub-firebase.json")
firebase_admin.initialize_app(cred, {
    'storageBucket' : 'rattler-notehub.appspot.com' #reference to the default storage bucket
})
db = firestore.client()


def upload_to_firebase(file):
    # Upload the file to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(file.split('/')[-1])  # Use only the filename as the destination in Firebase Storage
    blob.upload_from_filename(file)

    file_path = blob.name
    encoded_file_path = quote(file_path, safe='')

    bucket_name = "rattler-notehub.appspot.com"
    url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_file_path}?alt=media"

    add_note_to_db(url)

    return url




"""
# testing
if __name__ == '__main__': 
    file_path = ""
    uploaded_url = upload_to_firebase(file_path)
    print("File uploaded successfully. URL:", uploaded_url)
"""