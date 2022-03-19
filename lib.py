import re
import sys

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder


class PreprocessDataframe(TransformerMixin):
    def fit(self, df, _):
        # Drop random/singular columns
        # self.mask = [bool(pd.Series(col).dropna().size) for col, s in X.T]
        self.drop_cols = df.columns[df.isna().all(axis=0)]
        print('Drop cols', self.drop_cols, file=sys.stderr)
        return self

    def transform(self, df: pd.DataFrame):
        assert (df.iloc[:, 0].str.count(' ') == 2).all()
        df = df.drop(columns=df.columns[0])  # process pid, container id/image

        return df.drop(columns=self.drop_cols)


class PreprocessText(TransformerMixin):
    fit = lambda x, *_: x

    def _fix(self, s):
        s = re.sub(r'(?<![.:\d])[a-f\d\[\]]+(:+[a-f\d\[\]]+)+|\d+([.:-]+\d+){2,4}', ' ', s)  # IP:port
        return s

    assert not _fix(None, '''
        123.123.123.123:1234
        123:[fab:12e:123:123]:1234
    ''').strip()

    def transform(self, X):
        Xt = [self._fix(s) for s in X]
        return Xt


class Transformer(TransformerMixin):
    CATEGORICAL_WEIGHT = 30

    def fit(self, df, _):
        transformers = []
        for i, (_, s) in enumerate(df.items()):
            n_words = s.fillna('').astype(str).str.count(r'\b\w+')
            assert n_words.mean() > 0
            if n_words.mean() <= 1:
                print(i, n_words.mean(), np.unique(n_words), sep='\t')
                transformers.append((
                    str(i),
                    OneHotEncoder(handle_unknown='ignore', dtype=np.int8),
                    [i] * self.CATEGORICAL_WEIGHT,
                ))
            else:
                n_features = round(max(5, min(50, n_words.median() * 5)))
                print(i, f'{n_words.mean():.2f}', n_features, sep='\t')
                transformers.append((
                    str(i),
                    make_pipeline(
                        PreprocessText(),
                        HashingVectorizer(
                            n_features=n_features,
                            token_pattern=r'[>\w-]+',
                            ngram_range=(1, 2),
                            lowercase=False,
                            alternate_sign=False,
                            norm=None,
                            dtype=np.uint8,
                        ),
                    ),
                    i
                ))
        self.transformer = ColumnTransformer(
            transformers=transformers,
            # n_jobs=-1,
        )
        X = df.fillna('').astype(str).values
        self.transformer.fit(X)
        return self

    def transform(self, df):
        X = df.fillna('').astype(str).values
        Xt = self.transformer.transform(X)
        assert Xt.size, Xt
        return Xt

