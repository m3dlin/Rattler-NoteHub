from dotenv import load_dotenv
load_dotenv()
import os
from googleapiclient.discovery import build
import requests
import subprocess

api_key = os.getenv('API_KEY')
service = build("drive", "v3", developerKey=api_key)

file_id = ""

url = f"https://www.googleapis.com/drive/v3/files/{file_id}?key={api_key}"