import argparse
import sys
import os

import pandas as pd

import processing as prc
import utilities as util


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


args = parse_args()
# initialiseer de variabelen voor later
match args.plot:
    case 'bar':
        fulldata = {}
    case 'line':
        fulldata = pd.DataFrame()

current_chunk = 0
for un_proccesed_chunk in pd.read_json(args.file,
                                       lines=True,
                                       chunksize=args.chunksize):
    util.verboseprint(f"Starting preprocessing for chunk {current_chunk}",
                      args)
    chunk = prc.preprocess(un_proccesed_chunk, args)
    util.verboseprint(f"Finished Preprocessing for chunk {current_chunk}\n"
                      f"Starting processing for chunk {current_chunk}", args)

    fulldata = prc.process(chunk, fulldata, args)
    util.verboseprint(f"Finished processing for chunk {current_chunk}", args)
    current_chunk += 1

# Checkt of er nog data over is gebleven
if ((isinstance(fulldata, dict) and not fulldata) or
        (isinstance(fulldata, pd.DataFrame) and fulldata.empty)):
    print('No data is left. Have you set your filters?')
    sys.exit(1)

prc.post_process(fulldata, args)
