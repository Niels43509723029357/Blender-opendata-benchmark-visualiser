import argparse

import pandas as pd
import matplotlib.pyplot as plt

# Zet maximum columns omhoog om het makkelijker te maken voor debugging
pd.options.display.max_columns = 32

# Regelt het parsen van argumenten met de argparse library
parser = argparse.ArgumentParser(description='hello world!')

parser.add_argument('file', type=str,
                    help='The relative or absolute file path'
                         ' to the json lines file containing the dataset')
parser.add_argument('-d', '--device', type=str, nargs='+',
                    help='Sets a filter'
                         ' for the devices used in the benchmark.'
                         'Accepts multiple arguments. Space separated')
parser.add_argument('-s', '--scene', type=str,
                    help='Sets a filter'
                         'for the scene used in the benchmark')
args = parser.parse_args()


data = pd.read_json(args.file, lines=True)
# Zorgt ervoor dat we de belangrijke data hebben in aparte columns
df = pd.json_normalize(data.explode('data')['data'])
# Zorgt ervoor dat de hardware die gebruikt wordt voor de benchmark,
# er apart staat in een kolom ipv een column met arrays
device_info = pd.json_normalize(df['device_info.compute_devices'].str[0])
device_info = device_info[['name']]
df = df.drop(columns=['device_info.compute_devices'])
df['device_info.compute_device'] = device_info['name']


# Filtert devices indien nodig
if args.device:
    df = df[df['device_info.compute_device'].isin(args.device)]
    if df.empty:
        print("No entries match the filters")
        exit()

# Filtert scenes indien nodig
if args.scene:
    df = df[df['scene.label'] == args.scene]
    if df.empty:
        print('No entries match the filters')
        exit()



print(df.tail())
