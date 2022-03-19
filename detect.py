#!/usr/bin/env python3
import pickle
import sys
from io import StringIO

import pandas as pd

if len(sys.argv) != 3:
    sys.exit(f'Usage: {sys.argv[0]} INPUT_TSV MODEL_PICKLE')

stdin = sys.stdin if sys.argv[1] == '-' else open(sys.argv[1])
model = pickle.load(open(sys.argv[2], 'rb'))

try:
    buffer = []
    for line in stdin:
        buffer.append(line)
        try:
            line = ' '.join(buffer[:-1]) + buffer[-1]
            df = pd.read_csv(StringIO(line), sep='\t', header=None)
        except pd.errors.EmptyDataError as e:
            print(f'{e.__class__.__name__}: {e}', file=sys.stderr)
            buffer = []
            continue
        except pd.errors.ParserError as e:
            # Try after adding another line
            continue
        else:
            buffer = []
        anomaly = model.predict(df)[0] == -1
        if anomaly:
            print(line, end='')
        # print(f'anomaly={model.score_samples(df)}', line, sep='\t', end='', file=sys.stderr)
        print(f'anomaly={anomaly}', line, sep='\t', end='', file=sys.stderr)
except:
    raise
