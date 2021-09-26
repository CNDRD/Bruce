import pyrebase
import json
import os
from dotenv import load_dotenv
load_dotenv()

firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
  #"serviceAccount": "serviceAccountKey.json"}
db = pyrebase.initialize_app(firebase_config).database()
