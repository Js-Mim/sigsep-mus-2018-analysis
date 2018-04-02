from pathlib import Path
from pandas.io.json import json_normalize
import pandas as pd
import json
import argparse


def museval2df(json_path):
    with open(json_path) as json_file:
        json_string = json.loads(json_file.read())
        df = json_normalize(
            json_string['targets'],
            ['frames'],
            ['name']
        )
        df = pd.melt(
            pd.concat(
                [
                    df.drop(['metrics'], axis=1),
                    df['metrics'].apply(pd.Series)
                ],
                axis=1
            ),
            var_name='metric',
            value_name='score',
            id_vars=['time', 'name'],
            value_vars=['SDR', 'SAR', 'ISR', 'SIR']
        )
        df['track'] = json_path.stem
        return df


def aggregate(input_dirs, output_path=None):
    data = []
    for path in input_dirs:
        p = Path(path)
        print(p.stem)
        if p.exists():
            json_paths = p.glob('**/*.json')
            for json_path in json_paths:
                df = museval2df(json_path)
                df['estimate'] = p.stem
                data.append(df)

    df = pd.concat(data, ignore_index=True)
    if output_path is not None:
        df.to_pickle(output_path)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate Folder')
    parser.add_argument(
        'submission_dirs',
        help='directories of submissions',
        nargs='+',
        type=str
    )

    parser.add_argument(
        '--out',
        help='saves dataframe to disk',
        type=str
    )

    args = parser.parse_args()
    df = aggregate(args.submission_dirs, output_path=args.out)
