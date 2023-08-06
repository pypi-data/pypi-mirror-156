# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anti_clustering']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.3,<1.23.0',
 'ortools==9.3.10497',
 'pandas>=1.3.2,<1.4.0',
 'scikit-learn>=1.1.1,<1.2.0',
 'scipy>=1.7.1,<1.8.0']

setup_kwargs = {
    'name': 'anti-clustering',
    'version': '0.1.0',
    'description': 'Generic Anti-Clustering',
    'long_description': "# Anti-clustering\n\nA generic Python library for solving the anti-clustering problem. While clustering algorithms will achieve high similarity within a cluster and low similarity between clusters, the anti-clustering algorithms will achieve the opposite; namely to minimise similarity within a cluster and maximise the similarity between clusters.\nCurrently, a handful of algorithms are implemented in this library:\n* An exact approach using a BIP formulation.\n* An enumerated exchange heuristic.\n* A simulated annealing heuristic.\n\nKeep in mind anti-clustering is computationally difficult problem and may run slow even for small instance sizes. The current ILP does not finish in reasonable time when anti-clustering the Iris dataset (150 data points).\n\nThe two former approaches are implemented as describing in following paper:\\\n*Papenberg, M., & Klau, G. W. (2021). Using anticlustering to partition data sets into equivalent parts.\nPsychological Methods, 26(2), 161–174. [DOI](https://doi.org/10.1037/met0000301). [Preprint](https://psyarxiv.com/3razc/)* \\\nThe paper is accompanied by a library for the R programming language: [anticlust](https://github.com/m-Py/anticlust).\n\nDifferently to the [anticlust](https://github.com/m-Py/anticlust) R package, this library currently only have one objective function. \nIn this library the objective will maximise intra-cluster distance: Euclidean distance for numerical columns and Hamming distance for categorical columns.\n\n## Use cases\nWithin software testing, anti-clustering can be used for generating test and control groups in AB-testing.\nExample: You have a webshop with a number of users. The webshop is undergoing active development and you have a new feature coming up. \nThis feature should be tested against as many different users as possible without testing against the entire user-base. \nFor that you can create a maximally diverse subset of the user-base to test against (the A group). \nThe remaining users (B group) will not test this feature. For dividing the user-base you can use the anti-clustering algorithms. \nA and B groups should be as similar as possible to have a reliable basis of comparison, but internally in group A (and B) the elements should be as dissimilar as possible.\n\nThis is just one use case, probably many more exists.\n\n## Usage\nThe input to the algorithm is a Pandas dataframe with each row representing a data point. The output is the same dataframe with an extra column containing integer encoded cluster labels. Below is an example based on the Iris dataset:\n```python\nfrom anti_clustering import ExactClusterEditingAntiClustering\nfrom sklearn import datasets\nimport pandas as pd\n\niris_data = datasets.load_iris(as_frame=True)\niris_df = pd.DataFrame(data=iris_data.data, columns=iris_data.feature_names)\n\nalgorithm = ExactClusterEditingAntiClustering()\n\ndf = algorithm.run(\n    df=iris_df,\n    numerical_columns=list(iris_df.columns),\n    categorical_columns=None,\n    num_groups=2,\n    destination_column='Cluster'\n)\n```\n\n## Contributions\nIf you have any suggestions or have found a bug, feel free to open issues. If you have implemented a new algorithm or know how to tweak the existing ones; PRs are very appreciated.\n\n## License\nThis library is licensed under the Apache 2.0 license.\n",
    'author': 'Matthias Als',
    'author_email': 'mata@ecco.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
