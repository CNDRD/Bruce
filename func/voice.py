from func.supabase import supabase
from datetime import datetime, timedelta
from pytz import timezone

local_timezone = 'Europe/Prague'


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


def get_day_time(today, yesterday, stayed, left) -> (int, int):
    cdt_data = supabase.from_('daily_voice').select('seconds').eq('date', today).execute()
    ydt_data = supabase.from_('daily_voice').select('seconds').eq('date', yesterday).execute()
    cdt = cdt_data.data[0]['seconds'] if cdt_data.data else 0
    ydt = ydt_data.data[0]['seconds'] if ydt_data.data else 0
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


def get_seconds_since_midnight_from_timestamp(leave_time) -> int:
    # name -_-
    leave_time = datetime.fromtimestamp(leave_time, tz=timezone(local_timezone))
    return int((leave_time - leave_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
