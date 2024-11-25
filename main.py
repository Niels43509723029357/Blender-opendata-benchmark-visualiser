import argparse
import sys
import os

import pandas as pd
import matplotlib.pyplot as plt


def parse_args():
    # Regelt het parsen van argumenten met de argparse library
    parser = argparse.ArgumentParser(
        description='This program generates graphs based on benchmark data'
                    ' from Blender\'s opendata project')
    parser.add_argument('file', type=str,
                        help='The relative or absolute file path'
                             ' to the json lines file containing the dataset')
    parser.add_argument('output_file', type=str,
                        help='The file to output the .svg to')
    parser.add_argument('--chunksize', '-cs', type=int,
                        help='The amount of lines loaded in memory at one time'
                             'Default = 30000', default=30000)
    parser.add_argument('--plot', '-p', choices=['bar', 'line'],
                        help='The type of plot to use')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Enables verbosity, giving more detailed output")
    parser.add_argument('--device', '-d', type=str, nargs='+',
                        help='Sets a filter'
                             ' for the devices used in the benchmark.'
                             'Space separated')
    parser.add_argument('--scene', '-s', type=str,
                        help='Sets a filter'
                             'for the scene used in the benchmark')
    parser.add_argument('-os', type=str,
                        nargs='+',
                        choices=['Windows',
                                 'Linux',
                                 'Darwin'],
                        help='Sets a filter'
                             'for the operating system the benchmark ran on')
    arguments = parser.parse_args()

    # bestandspad omzetten naar absoluut pad bij ~ en controleer of het bestaat
    arguments.file = os.path.expanduser(arguments.file)
    if not os.path.exists(arguments.file):
        print("Path doesn't exist.")
        sys.exit(1)

    # bestandspad omzetten naar absoluut pad, niet controleren of het bestaat
    # want dat doet het nog niet
    arguments.output_file = os.path.expanduser(arguments.output_file)

    # standaard 30k regels per chunk
    if not arguments.chunksize:
        print('No chunk size given, using default of 30k lines per chunk.')
    if arguments.chunksize <= 0:
        print(f'Chunksize of {arguments.chunksize} is invalid. '
              f'The chunksize has to be higher then 0.')
        sys.exit(1)
    return arguments


def preprocess(chunk):
    global current_chunk
    verboseprint(f'Starting preprocessing chunk {current_chunk}')

    # Zorgt ervoor dat we de belangrijke data hebben in aparte columns
    chunk = pd.json_normalize(chunk.explode('data')['data'])

    # Bij cpu's wordt de compute device weergegeven
    # als een list met voor elke core de naam van de cpu
    # Aangezien wij dit niet willen doen,
    # lossen wij dit op met een korte lambda functie
    chunk['device_info.compute_device'] = (
        chunk['device_info.compute_devices']
        .apply(
            lambda device: device[0]['name']
            if isinstance(device, list)
            else device))
    # Drop de oude kolom
    chunk = chunk.drop(columns=['device_info.compute_devices'])
    # Originele dataset bevat wat corrupte namen, dit haalt ze eruit door
    # simpelweg alle namen met non-printable characters eruit te vissen
    chunk = chunk[chunk['device_info.compute_device'].str.contains(
        '^[\x20-\x7E]+$',
        regex=True,
        na=False
    )]
    # Filtert devices indien nodig
    if args.device:
        chunk = chunk[chunk['device_info.compute_device'].isin(args.device)]

    # Filtert scenes indien nodig
    if args.scene:
        chunk = chunk[chunk['scene.label'] == args.scene]

    # Filtert os indien nodig
    if args.os:
        chunk = chunk[chunk['system_info.system'].isin(args.os)]

    verboseprint(f'Finished preprocessing chunk {current_chunk}')
    return chunk


def process(chunk):
    global current_chunk
    verboseprint(f'Starting processing Chunk {current_chunk}')
    global fulldata

    match args.plot:

        case 'bar':
            # We houden het totaal aan score bij per device in een dict,
            # zodat we aan het einde in de post_process functie het gemiddelde
            # kunnen berekenen.
            for device, group in chunk.groupby('device_info.compute_device'):
                totalofchunk = group['stats.render_time_no_sync'].sum()
                if device in fulldata:
                    total, count = fulldata[device]
                    fulldata[device] = (total + totalofchunk,
                                        count + len(group))
                else:
                    fulldata[device] = totalofchunk, len(group)
        case 'line':
            # We doen geen dingen met een lijngrafiek,
            # aangezien we dan alle data nodig hebben wanneer we het maken
            # Wel checken we eerst of fulldata leeg is
            # voordat we concat gebruiken omdat het later verandert hoe
            # het werkt met dtype assignment met lege kolommen
            if fulldata.empty:
                fulldata = chunk[['device_info.compute_device',
                                  'stats.render_time_no_sync',
                                  'timestamp']]
            else:
                fulldata = pd.concat([fulldata,
                                      chunk[['device_info.compute_device',
                                             'stats.render_time_no_sync',
                                             'timestamp']]])
    verboseprint(f'Processed chunk {current_chunk}')
    current_chunk += 1


def post_process(data):
    verboseprint('Making chart')
    match args.plot:
        case 'bar':
            # De uiteindelijke gemiddeldes berekenen
            for device, (total, benchmarks) in data.items():
                average = total / benchmarks
                data[device] = average
            plt.bar(data.keys(), data.values())

            # Extra dingen van pyplot voor behoorlijke grafiek
            plt.xticks(rotation=-40)
            plt.ylabel("Render time (lower is better)")
            plt.grid(True, axis="y")
            plt.title("Render time average per device")
            plt.tight_layout()

        case "line":
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            for device, group in data.groupby('device_info.compute_device'):
                verboseprint(f'Sorting device: {device}')
                group = group.sort_values('timestamp')
                verboseprint(f'Sorting done for device: {device}')
                plt.plot(group['timestamp'],
                         group['stats.render_time_no_sync'], label=device)
                verboseprint(f'Plotted graph for device: {device}')

            # Extra dingen van pyplot voor behoorlijke grafiek
            plt.legend()
            plt.grid(True)
            plt.xlabel('Time')
            plt.ylabel("Render time (lower is better")
            plt.title('Render time over time per device')
            plt.tight_layout()
    verboseprint("Saving chart")
    plt.savefig(args.output_file, format='svg')


def verboseprint(string):
    if args.verbose:
        print(string)


args = parse_args()
# initialiseer de variabelen voor later
match args.plot:
    case 'bar':
        fulldata = {}
    case 'line':
        fulldata = pd.DataFrame()

current_chunk = 1
for un_proccesed_chunk in pd.read_json(args.file,
                                       lines=True,
                                       chunksize=args.chunksize):
    process(preprocess(un_proccesed_chunk))

# Checkt of er nog data over is gebleven
if ((isinstance(fulldata, dict) and not fulldata) or
        (isinstance(fulldata, pd.DataFrame) and fulldata.empty)):
    print('No data is left. Have you set your filters?')
    sys.exit(1)

post_process(fulldata)
