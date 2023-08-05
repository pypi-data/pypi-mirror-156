import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.datasets import make_classification
from sklearn.datasets import make_regression

# TODO: Make use of the dummy data creator
#  from Amplo.Utils.testing import (DummyDataSampler, make_data, make_cat_data, make_num_data)
from Amplo.AutoML import FeatureProcessor


class TestFeatureProcessor:

    def test_regression(self):
        x, y = make_regression()
        x, y = pd.DataFrame(x, columns=[f'F{i}' for i in range(len(x[0]))]), pd.Series(y)
        fp = FeatureProcessor(max_lags=2, mode='regression')
        xt, sets = fp.fit_transform(x, y)

    def test_classification(self):
        x, y = make_classification()
        x, y = pd.DataFrame(x), pd.Series(y)
        fp = FeatureProcessor(max_lags=2, mode='classification')
        xt, sets = fp.fit_transform(x, y)

    def test_co_linearity(self):
        y = pd.Series(np.linspace(2, 100, 100))
        x = pd.DataFrame({'a': np.linspace(-4, 4, 100), 'b': np.linspace(-4, 4, 100)})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.coLinearFeatures) != 0, "Collinear feature not removed"

    def test_multiply_features(self):
        y = pd.Series(np.linspace(2, 100, 100))
        b = pd.Series(np.linspace(-4, 4, 100) ** 2)
        x = pd.DataFrame({'a': y / b, 'b': b})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.crossFeatures) != 0, "Multiplicative feature not spotted"

    def test_division(self):
        y = pd.Series(np.linspace(2, 100, 100))
        b = pd.Series(np.linspace(-4, 4, 100) ** 2)
        x = pd.DataFrame({'a': y * b, 'b': b})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.crossFeatures) != 0, "Division feature not spotted"

    def test_trigonometry(self):
        y = pd.Series(np.sin(np.linspace(0, 100, 100)))
        x = pd.DataFrame({'a': np.linspace(0, 100, 100)})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.trigonometricFeatures) != 0, "Trigonometric feature not spotted"

    def test_lagged(self):
        y = pd.Series(np.random.randint(0, 100, 100))
        x = pd.DataFrame({'a': np.roll(y, -5)})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.laggedFeatures) != 0, "Lagged feature not spotted"

    def test_diff(self):
        y = pd.Series(np.random.randint(1, 100, 100))
        x = pd.DataFrame({'a': np.cumsum(y)})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert len(fp.diffFeatures) != 0, "Difference feature not spotted"

    def test_select(self):
        n = 5000
        y = pd.Series(np.linspace(0, 100, n))
        x = pd.DataFrame({'a': y, 'b': np.random.normal(0, 5, n)})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert all(['a' in i and 'b' not in i for i in sets.values()]), f"Random Feature Selected: {sets}"

    def test_settings(self):
        y = pd.Series(np.random.randint(1, 100, 100))
        b = pd.Series(np.linspace(-4, 4, 100))
        x = pd.DataFrame({'a': np.cumsum(y), 'b': np.roll(y, -5), 'c': y / b, 'd': y * b})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        settings = fp.get_settings()
        fpn = FeatureProcessor(mode='regression')
        fpn.load_settings(settings)
        for k, v in sets.items():
            xtn = fpn.transform(x, k)
            assert len(v) == len(xtn.keys()), "Incorrect number of keys"
            assert all(xt[v].keys() == xtn.keys()), 'Keys are not correct'
            assert np.allclose(xt[v], xtn), 'Transformed data not consistent for {} set'.format(k)

    def test_get_required(self):
        y = pd.Series(np.linspace(2, 100, 100))
        b = pd.Series(np.linspace(-4, 4, 100) ** 2)
        x = pd.DataFrame({'a': y / b, 'b': b, 'c': b / 2})
        fp = FeatureProcessor(mode='regression')
        xt, sets = fp.fit_transform(x, y)
        assert set(fp.get_required_features(['a__x__b'])) == {'b', 'a'}

    def test_datetime(self):
        x = pd.DataFrame({
            'ts': pd.date_range(start=datetime.now(), periods=1000, freq='1s'),
            'noise': np.random.normal(0, 5, 1000),
        })
        y = pd.Series(np.linspace(0, 100, 1000))
        fp = FeatureProcessor(mode='regression', date_cols=['ts'])
        xt, sets = fp.fit_transform(x, y)
        print(sets)
