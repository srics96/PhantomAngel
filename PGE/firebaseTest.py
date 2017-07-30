import pyrebase

config = {
  "apiKey": "AIzaSyB4555K4PmN7z5oMFIIfu08HSV_NRReSZQ",
  "authDomain": "phantom-gab-engine.firebaseapp.com",
  "databaseURL": "https://phantom-gab-engine.firebaseio.com",
  "storageBucket": "phantom-gab-engine.appspot.com",
  "serviceAccount": "phantom-gab-engine-firebase-adminsdk-o9tcv-6faea27d58.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("sriablaze@gmail.com", "1234sri#")
db = firebase.database()
employee = {"name": "Sricharan", "email": "sricharanprograms@gmail.com"}
db.child("employees").push(employee, user['idToken'])