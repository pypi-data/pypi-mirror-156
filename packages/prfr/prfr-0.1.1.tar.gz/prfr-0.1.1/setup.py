# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prfr']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.1.0,<2.0.0',
 'numba>=0.55.1,<0.56.0',
 'numpy<1.22',
 'scipy>=1.8.0,<2.0.0',
 'sklearn>=0.0,<0.1',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'prfr',
    'version': '0.1.1',
    'description': '',
    'long_description': '# prfr\n\nProbabilistic random forest regressor: random forest model that accounts for errors in predictors and yields calibrated probabilistic predictions.\n\n## Installation\n\n```bash\npip install prfr\n```\n\n## Example usage\n\n```python\nimport numpy as np\nfrom prfr import ProbabilisticRandomForestRegressor, split_arrays\n\nx_obs = np.random.uniform(0., 10., size=10000).reshape(-1, 1)\nx_err = np.random.exponential(1., size=10000).reshape(-1, 1)\ny_obs = np.random.normal(x_obs, x_err).reshape(-1) * 2. + 1.\n\ntrain_arrays, test_arrays, valid_arrays = split_arrays(x_obs, x_err, y_obs, test_size=0.2, valid_size=0.2)\nx_train, x_err_train, y_train = train_arrays\nx_test, x_err_test, y_test = test_arrays\nx_valid, x_err_valid, y_valid = valid_arrays\n\nmodel = ProbabilisticRandomForestRegressor(n_estimators=250, n_jobs=-1)\nmodel.fit(x_train, y_train, eX=x_err_train)\nmodel.calibrate(x_valid, y_valid, eX=x_err_valid)\nmodel.fit_bias(x_valid, y_valid, eX=x_err_valid)\n\npred = model.predict(x_test, eX=x_err_test)\npred_bounds = np.quantile(pred, [0.16, 0.84], axis=1)\npred_mean = np.mean(pred, axis=1)\n\nprint(pred.shape)\n```\n',
    'author': 'Jeff Shen',
    'author_email': 'jshen2014@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
