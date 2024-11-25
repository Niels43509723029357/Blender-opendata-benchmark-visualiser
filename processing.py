import pandas as pd
import matplotlib.pyplot as plt


def preprocess(chunk, args):

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

    return chunk


def process(chunk, fulldata, args):

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
    return fulldata


def post_process(data, args):
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
                group = group.sort_values('timestamp')
                plt.plot(group['timestamp'],
                         group['stats.render_time_no_sync'], label=device)

            # Extra dingen van pyplot voor behoorlijke grafiek
            plt.legend()
            plt.grid(True)
            plt.xlabel('Time')
            plt.ylabel("Render time (lower is better)")
            plt.title('Render time over time per device')
            plt.tight_layout()
    plt.savefig(args.output_file, format='svg')
