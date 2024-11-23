import argparse
import sys
import os

import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.expand_frame_repr', False)
def parse_args():
    # Regelt het parsen van argumenten met de argparse library
    parser = argparse.ArgumentParser(description='hello world!')

    parser.add_argument('file', type=str,
                        help='The relative or absolute file path'
                             ' to the json lines file containing the dataset')
    parser.add_argument('-s', '--scene', type=str,
                        help='Sets a filter'
                             'for the scene used in the benchmark')
    parser.add_argument('-Cs', '--Chunksize', type=int,
                        help='The amount of lines loaded in memory at one time'
                             'Default = 30000', default=30000)
    parser.add_argument('--Plot', '-P', choices=['Bar', 'Time'],
                        help='Thhe type of plot to use')
    parser.add_argument('-d', '--device', type=str, nargs='+',
                        help='Sets a filter'
                             ' for the devices used in the benchmark.'
                             'Accepts multiple arguments if Plotting type supports it. '
                             'Space separated')
    args = parser.parse_args()
    file_path = os.path.expanduser(args.file)
    if not os.path.exists(file_path):
        print("Path doesn't exist.")
        sys.exit(1)
    # default of 30k lines per chunk
    if not args.Chunksize:
        print('No chunk size given, using default of 30k lines per chunk.')
    if args.Chunksize <= 0:
        print(f'Chunksize of {args.Chunksize} is invalid. The chunksize has to be higher then 0.')
        sys.exit(1)
    return args, file_path


# Bij CPU's wordt bij compute devices een array neergezet met elke core. Door de eerste te pakken, of bij gevallen met
# bijvoorbeeld een GPU of een enkele CPU core, de hele string, Dedupliceren wij dit
def pak_eerste_item(x):
    if isinstance(x, list):
        return x[0]['name']
    return x


def preprocess(chunk, args):
    global current_chunk
    print(f'Starting preprocessing chunk {current_chunk}')

    # Zorgt ervoor dat we de belangrijke data hebben in aparte columns
    chunk = pd.json_normalize(chunk.explode('data')['data'])
    # Zorgt ervoor dat de hardware die gebruikt wordt voor de benchmark,
    # er apart staat in een kolom ipv een column met arrays
    chunk['device_info.compute_device'] = (chunk['device_info.compute_devices'].apply(pak_eerste_item))
    chunk = chunk.drop(columns=['device_info.compute_devices'])
    # Originele dataset bevat wat corrupte namen, dit haalt ze eruit
    chunk = chunk[chunk['device_info.compute_device'].str.contains('^[\x20-\x7E]+$', regex=True, na=False)]

    # Filtert devices indien nodig
    if args.device:
        chunk = chunk[chunk['device_info.compute_device'].isin(args.device)]

    # Filtert scenes indien nodig
    if args.scene:
        chunk = chunk[chunk['scene.label'] == args.scene]

    print(f'Finished preprocessing chunk {current_chunk}')
    return chunk


def process(chunk, args):
    global current_chunk
    #global fulldata because bar plot needs to modify it when necesary
    print(f'Starting processing Chunk {current_chunk}')
    global fulldata

    match args.Plot:

        case 'Bar':


            for device, group in chunk.groupby('device_info.compute_device'):
                totalofchunk = group['stats.render_time_no_sync'].sum()
                if device in fulldata:
                    total, count = fulldata[device]
                    fulldata[device] = (total + totalofchunk, count + len(group))
                else:
                    fulldata[device] = totalofchunk, len(group)
        case 'Time':
            # no processing for time graph, since that requires all the data at one point for sorting it, meaning we can only do this at the end
            fulldata = pd.concat([fulldata, chunk[['device_info.compute_device', 'stats.render_time_no_sync', 'timestamp']]])

    current_chunk += 1
    print(f'Processed chunk {current_chunk}')


def post_process(data, args):
    print('Starting postprocessing')
    match args.Plot:
        case 'Bar':
            for device, (total, benchmarks) in fulldata.items():
                average = total / benchmarks
                fulldata[device] = average
            plt.bar(fulldata.keys(), fulldata.values())
            plt.tight_layout()
            plt.show()

        case "Time":
            for device, group in fulldata.groupby('device_info.compute_device'):
                plt.plot(group['timestamp'], group['stats.render_time_no_sync'], label=device)

            plt.legend()
            plt.grid(True)
            plt.xlabel('Time')
            plt.ylabel("Render time")
            plt.title('Render time over time per device')
            plt.tight_layout()
            plt.show()

current_chunk = 0



arguments, path = parse_args()
#initialize the variable for the output, depending on plot type
match arguments.Plot:
    case 'Bar':
        fulldata = {}
    case 'Time':
        fulldata = pd.DataFrame(columns=['device_info.compute_device', 'stats.render_time_no_sync', 'timestamp'])

for un_proccesed_chunk in pd.read_json(path, lines=True, chunksize=arguments.Chunksize):
    process(preprocess(un_proccesed_chunk, arguments), arguments)

if fulldata.empty:
    print('No data is left. Have you set your filters?')
    sys.exit(1)

post_process(fulldata, arguments)
