# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skillsnetwork',
 'skillsnetwork.cvstudio',
 'skillsnetwork.cvstudio.download_all',
 'skillsnetwork.cvstudio.download_model',
 'skillsnetwork.cvstudio.ping',
 'skillsnetwork.cvstudio.report',
 'skillsnetwork.cvstudio.upload_model']

package_data = \
{'': ['*']}

install_requires = \
['ipython', 'ipywidgets>=7,<8', 'requests>=2,<3', 'tqdm>=4,<5']

extras_require = \
{'regular': ['ibm-cos-sdk>=2,<3']}

setup_kwargs = {
    'name': 'skillsnetwork',
    'version': '0.19.3',
    'description': 'Library for working with Skills Network',
    'long_description': '# Skills Network Python Library\n\nA python library for working with [Skills Network](https://skills.network).\n\n## Installation\n### JupyterLite Installation\n```bash\npip install skillsnetwork\n```\n\n### Regular Installation (JupyterLab, CLI, etc.)\n```bash\npip install skillsnetwork[regular]\n```\n\n## Usage\n\n## JupyterLab / JupyterLite on Skills Network Labs\nThe `skillsnetwork` package provides a unified interface for reading/downloading\nfiles in JupyterLab and JupyterLite.\n\n### Reading a file\n```python\ncontent = await skillsnetwork.read("https://example.com/myfile")\n```\n\n### Downloading a file\n```python\nawait skillsnetwork.download("https://example.com/myfile", filename=filename)\nwith open(filename, "r") as f:\n    content = f.read()\n```\n\n### Preparing a dataset (downloading, unzipping, and unarchiving)\n```python\nawait skillsnetwork.prepare("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz")\n```\n\n#### Example migration from old method\n##### Old methods\n\n###### Naively downloading and unzipping/untarring (runs very slowly on Skills Network Labs):\n```python\n! wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz\nprint("Images dataset downloaded!")\n!tar -xf images.tar.gz\nprint("Images dataset unzipped!")\n```\n\n###### Old workaround for better performance (this is confusing to users)\n```python\n! wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz\nprint("Images dataset downloaded!")\n!tar -xf images.tar.gz -C /tmp\n!rm -rf images\n!ln -sf /tmp/images/ .\nprint("Images dataset unzipped!")\n```\n\n\n##### New and improved method\n```python\nawait skillsnetwork.prepare("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz")\n```\n\n\n\n## CV Studio\n\n### Environment Variables\n- `CV_STUDIO_TOKEN`\n- `CV_STUDIO_BASE_URL`\n- `IBMCLOUD_API_KEY`\n\n### Python Code example\n```python\nfrom datetime import datetime\nimport skillsnetwork.cvstudio\ncvstudio = skillsnetwork.cvstudio.CVStudio(\'token\')\n\ncvstudio.report(started=datetime.now(), completed=datetime.now())\n\ncvstudio.report(url="http://vision.skills.network")\n```\n\n### CLI example\n```bash\npython -m \'skillsnetwork.cvstudio\'\n```\n\n## Contributing\nPlease see [CONTRIBUTING.md](https://github.com/ibm-skills-network/skillsnetwork-python-library/blob/main/CONTRIBUTING.md)\n',
    'author': 'Bradley Steinfeld',
    'author_email': 'bs@ibm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
