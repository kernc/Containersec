#!/usr/bin/env python3
import pickle
import sys

import pandas as pd
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import SGDOneClassSVM
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import make_pipeline

from lib import PreprocessDataframe, Transformer

if not len(sys.argv) == 3:
    sys.exit(f'Usage: {sys.argv[0]} INPUT_TSV MODEL_PICKLE')
stdin = sys.stdin if sys.argv[1] == '-' else open(sys.argv[1])
try:
    # df = pd.read_csv(StringIO(sys.stdin.read()), sep='\t', header=None)
    df = pd.read_csv(stdin, sep='\t', dtype=str, header=None)
except pd.errors.EmptyDataError as e:
    sys.exit(f'{e.__class__.__name__}: {e}')

print(df)

model = make_pipeline(
    PreprocessDataframe(),
    Transformer(),
    Nystroem(n_components=200, kernel='linear'),
    RandomizedSearchCV(
        scoring='accuracy',
        estimator=SGDOneClassSVM(nu=.3, learning_rate='invscaling', eta0=2, verbose=True,),
        param_distributions={
            'nu': [.5, .3, .1],
            'eta0': [2, 1, .5],
        },
    ),
)

model.fit(df, [1]*len(df))

pred = model.predict(df)
print(pred, file=sys.stderr)
assert len(set(pred)) == 1, pred

with open(sys.argv[2], 'wb') as fd:
    pickle.dump(model, fd, protocol=pickle.HIGHEST_PROTOCOL)
