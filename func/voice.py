import pyrebase, datetime, yaml, json
from pytz import timezone

config = yaml.safe_load(open('config.yml'))
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


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

def get_current_day_time(curr_year, today, stayed):
    cdt = db.child('voice').child(curr_year).child('day').child(today).get().val()
    if cdt is None: cdt = 0
    return cdt + stayed

def get_user_total(atvs, stayed):
    if atvs is None: atvs = 0
    return atvs + stayed

def get_today_tz():
    # Timezone-aware date string
    return datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')

def get_curr_year_tz():
    # Timezone-aware date year
    return datetime.datetime.now(timezone('Europe/Prague')).year

def get_yearly_user_data(curr_year, uid):
    yud = db.child('voice').child(curr_year).child('total').child(uid).get().val()
    if yud is None:
        yearVoice = 0
        yearLVS = 0
    else:
        yearVoice = yud.get('voice')
        yearLVS = yud.get('lvs')

    return yearVoice, yearLVS
