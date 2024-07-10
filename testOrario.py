"""
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

"""


from datetime import datetime, time, timedelta
import time as time_module
import pytz


# Get the timezone object for New York
tz_NY = pytz.timezone('America/New_York') 

# Get the current time in New York
datetime_NY = datetime.now(tz_NY)

print(datetime_NY.hour, datetime_NY.minute, datetime_NY.second)

# Format the time as a string and print it
print("NY time:", datetime_NY.strftime("%H:%M:%S"))


if (datetime_NY.hour >= 3) & (datetime_NY.hour < 9):
    if (datetime_NY.hour == 3):
        if datetime_NY.minute >= 30:
            print("It's Okay!")



def wait(target_time):
    try:
        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        sleep_duration = (target_time - datetime_NY).total_seconds()

        print(sleep_duration)

        if sleep_duration > 0:
            print(f"Il programma si interromperà fino a: {target_time}")
            time_module.sleep(sleep_duration)
            print("Il programma ha ripreso l'esecuzione.")
        else:
            print("Il tempo target è già passato.")
    except Exception as e:
        print(f"Errore durante l'attesa: {e}")


if __name__ == '__main__':
    try:
        specified_time = time(4, 56)  # Ad esempio, 9:30

        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        target_time = tz_NY.localize(datetime.combine(datetime_NY.date(), specified_time))
        
        print(target_time)
        print()

        # Se l'orario specificato è già passato per oggi, imposta l'orario per il giorno successivo
        if target_time < datetime_NY:
            target_time += timedelta(days=1)

        wait(target_time)

    except Exception as e:
        print(f"Errore durante l'impostazione dell'orario target: {e}")



"""
# Get the timezone object for London
tz_London = pytz.timezone('Europe/London')

# Get the current time in London
datetime_London = datetime.now(tz_London)

# Format the time as a string and print it
print("London time:", datetime_London.strftime("%H:%M:%S"))

#print(set(pytz.all_timezones_set)  )

# Get the timezone for Italy
tz_Italy = pytz.timezone('Europe/Rome')

# Get the current time in Italy
datetime_Italy = datetime.now(tz_Italy)

# Format the time as a string and print it
print("Rome time:", datetime_Italy.strftime("%H:%M:%S"))

"""
