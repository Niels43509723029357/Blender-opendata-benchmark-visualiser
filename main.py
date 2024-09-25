import argparse
import pandas as pd
import matplotlib as plt
# Zet maximum columns omhoog om het makkelijker te maken voor debugging
pd.options.display.max_columns = 32

# regelt het parsen van argumenten
parser = argparse.ArgumentParser(description='hello world!')
parser.add_argument('-f', '--file', required=True, type=str,
                    help='The relative or absolute file path'
                         ' to the json lines file containing the dataset')
parser.add_argument('-d', '--device', type=str,
                    help='This sets a filter'
                         ' for which device was used for the benchmark')
args = parser.parse_args()


data = pd.read_json(args.file, lines=True)
# zorgt ervoor dat we de belangrijke data hebben in aparte columns
df = pd.json_normalize(data.explode('data')['data'])
# zorgt ervoor dat de hardware die gebruikt wordt voor de benchmark,
# er apart staat in een kolom ipv een column met arrays
device_info = pd.json_normalize(df['device_info.compute_devices'].str[0])
device_info = device_info[['name']]
df = df.drop(columns=['device_info.compute_devices'])
df['device_info.compute_device'] = device_info['name']


# het filteren van devices
if args.device:
    df = df[df['device_info.compute_device'] == args.device]
    if df.empty:
        print("No entries match the filters")


print(df)
