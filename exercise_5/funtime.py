from datetime import datetime
import time

todays_date = datetime.now()
date_string = todays_date.isoformat()
timestamp = time.time()
print(timestamp)
also_todays_date = datetime.fromtimestamp(timestamp)
print(also_todays_date)