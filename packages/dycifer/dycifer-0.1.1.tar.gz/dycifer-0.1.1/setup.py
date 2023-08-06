# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dycifer']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.7,<4.0.0',
 'argparse>=1.4.0,<2.0.0',
 'colorama>=0.4.5,<0.5.0',
 'loguru>=0.6.0,<0.7.0',
 'matplotlib>=3.5.2,<4.0.0',
 'modelling-utils>=0.2.11,<0.3.0',
 'numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'plotext>=5.0.2,<6.0.0',
 'pyfiglet>=0.8.post1,<0.9',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['dycifer = dycifer.dycifer:cli']}

setup_kwargs = {
    'name': 'dycifer',
    'version': '0.1.1',
    'description': 'DYCIFER (Dynamic Circuits Performance Evaluation Tool) is a tool dedicated to the calculation of the performance indicators of integrated circuits operating at relatively high frequencies.',
    'long_description': '![GitHub Workflow Status](https://img.shields.io/github/workflow/status/das-dias/dyciferpy/dycifer)\n![GitHub](https://img.shields.io/github/license/das-dias/dyciferpy)\n![GitHub issues](https://img.shields.io/github/issues/das-dias/dyciferpy)\n![GitHub package.json version (branch)](https://img.shields.io/github/package-json/v/das-dias/dyciferpy/master)\n![GitHub last commit](https://img.shields.io/github/last-commit/das-dias/dyciferpy)\n\n![banner](./docs/imgs/DYCIFER2.png)\n\n``` Dynamic Circuit Performance Evaluation Tool (DYCIFER) ```\n\n is a tool written in ```Python``` that allows for the extraction of the Performance Indicators of Dynamic Integrated Circuits. Through the analysis of each system\'s signals (both input and output), the tool will be able to extract indicators such as the *Total Harmonic Distortion* (THD) or *Signal to Noise & Distortion Ratio* (SNDR) of dynamic integrated circuit.\n\n## How does it work\nAny integrated circuit designer can simulate the time response of an implemented system through a *Transient Analysis*, which is a basic concept of Electric Circuits Theory. The exported data to Comma Separated Values files (.CSV) can be parsed as input to the tool.\nIn the examples provided, ®Cadence Virtuoso\'s time response simulator was used to obtain some of the time response data.\n\n![fft-algo](./docs/imgs/fft-algo-inverted.png)\n\nFrom the simulated time response data of the system we want to analyze, the [*Fast Fourier Transform* (FFT)](URL "brilliant.org/wiki/discrete-fourier-transform/") (core) algorithm is used to enable the extraction of all the *Dynamic Circuit Performance Indicators* listed in the table below. From these indicators, an integrated circuit designer can eccurately measure the performance of the designed system.\n\n| Performance Indicator | Description |\n| --- | --- |\n| [Signal Strength](./docs/indicators.md) | Power of the analysed signal |\n| [DC Signal Strength](./docs/indicators.md) | Power of the DC component of the analysed signal |\n| [ENOB](./docs/enob.md) | Effective Number of Bits |\n| [SFDR](./docs/indicators.md) | Spurious Free Dynamic Range |\n| [SNR](./docs/indicators.md) | Signal to Noise Ratio |\n| [THD](./docs/indicators.md) | Total Harmonic Distortion |\n| [SNDR](./docs/indicators.md) | Signal to Noise & Distortion Ratio |\n| [HD2](./docs/indicators.md) | 2nd Order Harmonic Distortion Ratio |\n| [HD3](./docs/indicators.md) | 3rd Order Harmonic Distortion Ratio |\n| [Gain](./docs/indicators.md) | Power Ratio between the Output and Input signals |\n| [Rise Time [90%]](./docs/rise-time.md) | The total time it takes the signal to rise from 10% up to 90% of its total amplitude - only important in pulse responses or pulse modulated signals. |\n| | |\n\n## Dependencies\n\n- [Poetry](URL "https://python-poetry.org/docs/") - ```Poetry``` is the default ®Python package manager, and it allows to easily deploy and install any project or package written in Python language.\n\nOther [package dependencies](./docs/dependencies.md)\n\n## Installation \n\nIt is highly recommended to use ```Poetry``` in order to install ```DYCIFER``` because it will automatically setup the virtual environment and package dependencies necessary to run this tool. \\\nFirst of all, ```git-clone``` this repository into a directory:\n\n![git-clone](./docs/imgs/carbon-gitclone.png)\n```\ngit clone https://github.com/das-dias/dyciferpy.git\n```\n\nAlternatively, you can [download](URL "https://github.com/das-dias/dyciferpy/archive/refs/heads/master.zip") this repo\'s ```.zip``` file and extract it into a personal directory, if you don\'t have [git](URL "https://git-scm.com/book/en/v2/Getting-Started-Installing-Git") installed in your machine.\n\nNext, using ```Poetry```, inside the downloaded repository directory, run the installation command:\n\n![poetry-install](.docs/../docs/imgs/carbon-poetryinstall.png)\n```\npoetry install\n```\n## Usage\n### Asking for help\n\n```\npoetry run dycifer | -h | --help\n```\n\n![General Help](.docs/../docs/imgs/general-help.gif)\n\n```DYCIFER``` is a tool designed to run on the console, and as such it features a neat-looking *Command Line Interface* (CLI) that allows for an easy interaction with its sub-frameworks:\n\n- Mixed-signals Integrated Circuits dedicated framework\n- Analog Integrated Circuits dedicated framework\n\n### Mixed Signals Integrated Circuit Performance Analysis\n\n```\npoetry run dycifer mixedsignals | -h | --help\n```\n\n![Mixed-Signals Help](.docs/../docs/imgs/mixedsignals-help.gif)\n\nThis sub-framework is mainly dedicated to provide automated performance analysis to the following systems:\n\n- Analog-to-Digital Converters (ADC) (considering parallel output bit lines)\n- Digital-to-Analog Converters (DAC) <span style="color:red"> (NOT IMPLEMENTED YET) </span>\n- $\\Sigma \\Delta$ (Sigma-Delta) ADC (considering serial [*Pulse Width Modulated*](URL "https://en.wikipedia.org/wiki/Pulse-width_modulation") output signal line) <span style="color:red"> (NOT IMPLEMENTED YET) </span>\n- $\\Sigma \\Delta$ DAC <span style="color:red"> (NOT IMPLEMENTED YET) </span>\n  \n### Analog Integrated Circuit Performance Analysis\n\n```\npoetry run dycifer analog | -h | --help\n```\n\n![Analog Help](.docs/../docs/imgs/analog-help.gif)\n\nThis sub-framework provides coverage to two classes of analog integrated systems:\n\n- Continuous Amplitude Output Systems (CAOS)\n- Discrete Amplitude Output Systems (DAOS)\n\nThe discrimination of analog systems in these two classes provide for powerful, simplified methods to retrieve the performance indicators of (e.g.)\n\n- Transient responses resembling square (or pulse) waves, or pulse modulated sinusoidal waves, regarding DAOS systems\n\n- Sinusoidal waves (impure/distorted/noisy or pure), regarding CAOS systems\n\n## Examples\n\nDetailed examples on the usage of this tool can be found in the following documents:\n\n**Performance Analysis**\n- [ADC Performance Analysis](./docs/adc-example.md)\n- [CAOS Amplifier Performance Analysis](./docs/caos-amplifier-example.md)\n- [DAOS Amplifier Performance Analysis](./docs/daos-amplifier-example.md)\n  \n**Saving Images and Performance Indicators**\n- [Saving Tables](./docs/saving-tables.md)\n- [Saving Images](./docs/saving-images.md)',
    'author': 'Diogo André S. Dias',
    'author_email': 'das.dias6@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/das-dias/dyciferpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
