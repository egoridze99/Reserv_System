from datetime import timedelta, time, datetime

from utils.convert_tz import convert_tz


def get_shift_date(date_str: str, timezone: str, duration: int):
    if date_str is None:
        return None
    
    try:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        date = convert_tz(date, timezone, False)
        finish_date = date + timedelta(hours=duration)

        if finish_date.time() < time(8) and date.date() == finish_date.date():
            return (date - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

        return date.date().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error in get_shift_date: {e}")
