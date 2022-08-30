from func.firebase_init import db
from datetime import datetime, timedelta
from pytz import timezone
import yaml

local_timezone = yaml.safe_load(open("config.yml")).get("local_timezone")


def get_stay_time(curr_year, uid, now) -> int:
    # Get the time user joined at, delete it, calculate how long they stayed for
    joined_at = db.child("voice").child(curr_year).child("in").child(uid).get().val()
    db.child("voice").child(curr_year).child("in").child(uid).remove()
    return now - joined_at


def get_yearly_total(stayed, tv) -> int:
    if tv is None:
        tv = 0
    return stayed + tv


def get_yearly_lvs(stayed, current_lvs) -> int:
    if current_lvs is None:
        current_lvs = 0

    if stayed > current_lvs:
        return stayed
    return current_lvs


def get_day_time(curr_year, today, yesterday, stayed, left) -> (int, int):
    cdt = db.child("voice").child(curr_year).child("day").child(today).get().val() or 0
    ydt = db.child("voice").child(curr_year).child("day").child(yesterday).get().val() or 0
    since_mid = get_seconds_since_midnight_from_timestamp(left)

    if stayed > since_mid:
        stayed -= since_mid
        return (cdt + since_mid), (ydt + stayed)
    else:
        return (cdt + stayed), ydt


def get_user_total(atvs, stayed) -> int:
    if atvs is None:
        atvs = 0
    return atvs + stayed


def get_today_tz() -> str:
    # Timezone-aware date string
    return datetime.now(timezone(local_timezone)).strftime("%Y-%m-%d")


def get_yesterday_tz() -> str:
    # Timezone-aware date string
    return (datetime.now(timezone(local_timezone)) - timedelta(days=1)).strftime("%Y-%m-%d")


def get_curr_year_tz() -> int:
    # Timezone-aware date year
    return datetime.now(timezone(local_timezone)).year


def get_yearly_user_data(curr_year, uid) -> (int, int):
    yud = db.child("voice").child(curr_year).child("total").child(uid).get().val()
    if yud is None:
        year_voice = 0
        year_lvs = 0
    else:
        year_voice = yud.get("voice")
        year_lvs = yud.get("lvs")
    return year_voice, year_lvs


def get_seconds_since_midnight_from_timestamp(leave_time) -> int:
    # name -_-
    leave_time = datetime.fromtimestamp(leave_time, tz=timezone(local_timezone))
    return int((leave_time - leave_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
