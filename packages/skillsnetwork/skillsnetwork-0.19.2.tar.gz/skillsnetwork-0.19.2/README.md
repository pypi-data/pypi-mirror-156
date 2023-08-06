# Skills Network Python Library

A python library for working with [Skills Network](https://skills.network).

## Installation
### JupyterLite Installation
```bash
pip install skillsnetwork
```

### Regular Installation (JupyterLab, CLI, etc.)
```bash
pip install skillsnetwork[regular]
```

## Usage

## JupyterLab / JupyterLite on Skills Network Labs
The `skillsnetwork` package provides a unified interface for reading/downloading
files in JupyterLab and JupyterLite.

### Reading a file
```python
content = await skillsnetwork.read("https://example.com/myfile")
```

### Downloading a file
```python
await skillsnetwork.download("https://example.com/myfile", filename=filename)
with open(filename, "r") as f:
    content = f.read()
```

### Preparing a dataset (downloading, unzipping, and unarchiving)
```python
await skillsnetwork.prepare("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz")
```

#### Example migration from old method
##### Old methods

###### Naively downloading and unzipping/untarring (runs very slowly on Skills Network Labs):
```python
! wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz
print("Images dataset downloaded!")
!tar -xf images.tar.gz
print("Images dataset unzipped!")
```

###### Old workaround for better performance (this is confusing to users)
```python
! wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz
print("Images dataset downloaded!")
!tar -xf images.tar.gz -C /tmp
!rm -rf images
!ln -sf /tmp/images/ .
print("Images dataset unzipped!")
```


##### New and improved method
```python
await skillsnetwork.prepare("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-ML0187EN-SkillsNetwork/labs/module%203/images/images.tar.gz")
```



## CV Studio

### Environment Variables
- `CV_STUDIO_TOKEN`
- `CV_STUDIO_BASE_URL`
- `IBMCLOUD_API_KEY`

### Python Code example
```python
from datetime import datetime
import skillsnetwork.cvstudio
cvstudio = skillsnetwork.cvstudio.CVStudio('token')

cvstudio.report(started=datetime.now(), completed=datetime.now())

cvstudio.report(url="http://vision.skills.network")
```

### CLI example
```bash
python -m 'skillsnetwork.cvstudio'
```

## Contributing
Please see [CONTRIBUTING.md](https://github.com/ibm-skills-network/skillsnetwork-python-library/blob/main/CONTRIBUTING.md)
