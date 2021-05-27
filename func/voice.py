from datetime import datetime, timedelta
import pyrebase, json, os
from pytz import timezone

from dotenv import load_dotenv
load_dotenv()

config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(config).database()


def get_stay_time(curr_year, uid, now):
    # Get the time user joined at, delete it, calculate how long they stayed for
    joinedAt = db.child('voice').child(curr_year).child('in').child(uid).get().val()
    db.child('voice').child(curr_year).child('in').child(uid).remove()
    return now - joinedAt

def get_yearly_total(stayed, tv):
    if tv is None: tv = 0
    return stayed + tv

def get_yearly_lvs(stayed, current_lvs):
    if current_lvs is None: current_lvs = 0
    if stayed > current_lvs: return stayed
    return current_lvs

def get_day_time(curr_year, today, yesterday, stayed, left):
    cdt = db.child('voice').child(curr_year).child('day').child(today).get().val()
    ydt = db.child('voice').child(curr_year).child('day').child(yesterday).get().val()
    if cdt is None: cdt = 0
    if ydt is None: ydt = 0
    since_mid = get_seconds_since_midnight_from_timestamp(left)

    if stayed > since_mid:
        stayed -= since_mid
        return (cdt + since_mid), (ydt + stayed)
    else:
        return (cdt + stayed), ydt

def get_user_total(atvs, stayed):
    if atvs is None: atvs = 0
    return atvs + stayed

def get_today_tz():
    # Timezone-aware date string
    return datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')

def get_yesterday_tz():
    # Timezone-aware date string
    return (datetime.now(timezone('Europe/Prague')) - timedelta(days=1)).strftime('%Y-%m-%d')

def get_curr_year_tz():
    # Timezone-aware date year
    return datetime.now(timezone('Europe/Prague')).year

def get_yearly_user_data(curr_year, uid):
    yud = db.child('voice').child(curr_year).child('total').child(uid).get().val()
    if yud is None:
        yearVoice = 0
        yearLVS = 0
    else:
        yearVoice = yud.get('voice')
        yearLVS = yud.get('lvs')
    return yearVoice, yearLVS

def get_seconds_since_midnight_from_timestamp(leave_time):
    # name -_-
    leave_time = datetime.fromtimestamp(leave_time, tz=timezone('Europe/Prague'))
    return int((leave_time - leave_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
