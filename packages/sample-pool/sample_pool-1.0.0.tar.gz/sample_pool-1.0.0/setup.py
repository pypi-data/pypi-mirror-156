# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sample_pool']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'sample-pool',
    'version': '1.0.0',
    'description': 'A Python package for calculating aliquot size based on sample intensity',
    'long_description': '## Sample Pool Aliquot Size Calculator\n---\n\nThis package can be used to quickly calculate the ratio of 1 unit volume one may need to use so that all aliquots contain the same amount of proteomics content\n\n## Dependencies\n```toml\npandas = "^1.4.3"\n```\n\n## Usage \n```python\nimport pandas as pd\nfrom sample_pool.experiment import Experiment\n\n# Read tabulated text file containing the data\npath = r".\\RN_220625_Hippo-TiO2_15TMT_Minipool_PSMs.txt"\ndf = pd.read_csv(path, sep="\\t")\n\n# Create a variable with list of columns containing sample data\nsamples = [\n            "Abundance: 126",\n            "Abundance: 127N",\n            "Abundance: 127C",\n            "Abundance: 128N",\n            "Abundance: 128C",\n            "Abundance: 129N",\n            "Abundance: 129C",\n            "Abundance: 130N",\n            "Abundance: 130C",\n            "Abundance: 131N",\n            "Abundance: 131C",\n            "Abundance: 132N",\n            "Abundance: 132C",\n            "Abundance: 133N",\n            "Abundance: 133C"\n        ]\n\n# Create Experiment object with the dataframe and sample list as parameters\nexp = Experiment(df, samples)\n\n# Get aliquot size ratio as a dictionary with key being sample name and value being volume ratio\nsize = exp.get_aliquot_size(minimum_good_samples=10)\n\n# By default get_aliquot_size would use the sample with the lowest normalized sum intensity as the base for ratio calculation. To specify the sample, you can use based_on_sample parameter.\nsize = exp.get_aliquot_size(based_on_sample="Abundance: 127C", minimum_good_samples=10)\nprint(size)\n```\n',
    'author': 'Toan Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
