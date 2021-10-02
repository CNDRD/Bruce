def get_cicina_today(today, today_date):
    if today is None: return None
    xd = []
    for u in today:
        if today[u]['date'] == today_date:
            today[u].pop('date')
            xd.append(today[u])
    if xd == []: return None
    return xd
