from datetime import datetime
import pytz
from typing import Union, Any

def get_timezone(timezone: Union[str, pytz.timezone]) -> pytz.timezone:
    if isinstance(timezone, str):
        return pytz.timezone(timezone)
    return timezone

def convert_timezone_list(date_str:str, times_str:list, cal_tz:str, user_tz:Union[str, pytz.timezone]):
    # Prepare the new timezone
    cal_tz = pytz.timezone(cal_tz)
    
    # Prepare the local timezone
    user_tz: pytz.timezone = get_timezone(user_tz)

    if cal_tz == user_tz:
        return date_str, times_str

    new_times_str = []
    for time_str in times_str:
        # Combine date and time strings
        datetime_str = f'{date_str} {time_str}:00'
        
        # Create datetime object from the string
        dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        
        # Set the timezone to the local timezone
        dt = cal_tz.localize(dt)
        
        # Convert to the new timezone
        dt = dt.astimezone(user_tz)
        
        # Append the new time to the list
        new_times_str.append(dt.strftime('%H:%M'))
    
    # Return the new date and list of times
    return dt.strftime('%Y-%m-%d'), new_times_str

def format_time(time_str: str):
    # Check if input is in 12 hour format
    if "AM" in time_str or "PM" in time_str:
        dt = datetime.strptime(time_str, "%I:%M %p")
    else:
        dt = datetime.strptime(time_str, "%H:%M")
    
    # Format the datetime object back to a string in 24-hour format
    formatted_time_str = dt.strftime("%H:%M")

    return formatted_time_str

def convert_timezone(date_str:str, time_str:str, cal_tz:str, user_tz:Union[str, pytz.timezone]):
    # Prepare the new timezone
    cal_tz = pytz.timezone(cal_tz)
    
    # Prepare the local timezone
    user_tz: pytz.timezone = get_timezone(user_tz)

    new_times_str = []
    # Combine date and time strings
    datetime_str = f'{date_str} {format_time(time_str)}:00'
    
    # Create datetime object from the string
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    # Set the timezone to the local timezone
    dt = cal_tz.localize(dt)
    
    # Convert to the new timezone
    dt = dt.astimezone(user_tz)
    
    # Return the new date and list of times
    return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), dt

def create_tz_aware_datetime(date: str, time: str, timezone: Union[str, pytz.timezone]):
    # Combine date and time strings
    datetime_str = f'{date} {time}:00'
    
    # Create a datetime object from the string
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    # Localize the datetime object to the given timezone
    tz: pytz.timezone = get_timezone(timezone)
    dt = tz.localize(dt)
    
    return dt

if __name__ == '__main__':
    # Example usage:
    date_str = '2023-07-04'
    times_str = ['09:00', '09:30', '10:00']
    cal_tz = 'US/Pacific'
    user_tz = 'US/Eastern'

    new_date_str, new_times_str = convert_timezone_list(date_str, times_str, cal_tz, user_tz)
    print(new_date_str)
    print(new_times_str)

