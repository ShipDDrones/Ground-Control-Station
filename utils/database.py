# Imports
# -------------------------------------------------------------------------------
import pyrebase


class Database:

    def __init__(self):
        firebaseConfig = {
            "apiKey": "AIzaSyCXJGrSWThXQrt3ejiYFaEel22egsLl7GE",
            "authDomain": "shipdesp8266.firebaseapp.com",
            "databaseURL": "https://shipdesp8266-default-rtdb.firebaseio.com",
            "projectId": "shipdesp8266",
            "storageBucket": "shipdesp8266.appspot.com",
            "messagingSenderId": "779708755419",
            "appId": "1:779708755419:web:e4da7e43a7ef878b1dcbfe",
            "measurementId": "G-TKXJ9X9Y1Z"
        }
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = self.firebase.database()

    def isAttached(self):
        defibrilatorStatus = self.db.get()
        if list(defibrilatorStatus.val().values())[0] == 0:
            return False
        return True

