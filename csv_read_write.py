# TEST FILE
# writing, opening CSV file for faking the behavior of the SQL DB

from datetime import datetime
import pandas as pd

# 1 create a DF
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html -> from dictionnary

# append to those lists at each event
output_data = {'file_adress': [], 'event_time': [], 'event_type': [], 'date_time': [], 'vin': []}

# example of data, populate this test
event_times = [1627911594.889969, 1627911631.690163, 1627911915.89254, 1627911942.892979]
output_data['event_time'].extend(event_times)
number_of_events = len(event_times)
file_adress = 'test_adress'
event_type = 'car_crossing'
date_time = 'test_date'
vin = 'test_vin'
output_data['file_adress'].extend([file_adress] * number_of_events)
output_data['event_type'].extend([event_type] * number_of_events)
output_data['date_time'].extend([date_time] * number_of_events)
output_data['vin'].extend([vin] * number_of_events)
print(output_data)

# turn into DF
df = pd.DataFrame(data=output_data)
print(df)

# 2 write to a file output df.to_csv() method
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html


def file_namer(name, speed_t, prev_t, next_t):
    return f'{name}&create_on={datetime.now()}&s={speed_t}&p={prev_t}&n={next_t}.csv'


out_filename = file_namer('test_fake_db', '20ms', '20m', '10m')
print(out_filename)

df.to_csv(path_or_buf=out_filename)

# OK WORKS

# 3 open the file and read DF

df2 = pd.read_csv(out_filename)
print(df2)
print([df2['event_time'][i] for i in range(len(df2['event_time']))])
# OK the reading works smoothly with dictionnaries
# the times are still present
