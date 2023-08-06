import shutil
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import IPython
from tqdm.auto import tqdm

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
__version__ = importlib_metadata.version("skillsnetwork")

DEFAULT_CHUNK_SIZE = 8 << 10


class InvalidURLException(Exception):
    def __init__(self, url):
        self.url = url
        self.message = f"'{self.url}' is not a valid URL."
        super().__init__(self.message)


def is_jupyterlite():
    return IPython.sys.platform == "emscripten"


def url_is_valid(url):
    try:
        result = urlparse(url)
        # assume it's a valid URL if a URL scheme and netloc are successfully parsed
        return all([result.scheme, result.netloc])
    except:
        # if urlparse chokes on something, assume it's an invalid URL
        return False


async def _get_chunks(url, chunk_size):
    """
    Generator that yields consecutive chunks of bytes from URL 'url'
    :param url: The URL containing the data file to be read
    :param chunk_size: The size of each chunk (in no. of bytes).
    :returns: Generator yielding chunks of bytes from file at URL until done.
    :raises InvalidURLException: When URL is invalid.
    :raises Exception: When Exception encountered when reading from URL.
    """
    if not url_is_valid(url):
        raise InvalidURLException(url)
    desc = f"Downloading {Path(urlparse(url).path).name}"
    if is_jupyterlite():
        from js import fetch  # pyright: ignore
        from pyodide import JsException  # pyright: ignore

        try:
            response = await fetch(url)
            reader = response.body.getReader()
            pbar = tqdm(
                mininterval=1,
                desc=desc,
                total=int(response.headers.get("content-length", 0)),
            )
            while True:
                res = (await reader.read()).to_py()
                value, done = res["value"], res["done"]
                if done:
                    break
                value = value.tobytes()
                yield value
                pbar.update(len(value))
            pbar.close()
        except JsException:
            raise Exception(f"Failed to read dataset at {url}") from None
    else:
        import requests  # pyright: ignore
        from requests.exceptions import ConnectionError  # pyright: ignore

        try:
            with requests.get(url, stream=True) as response:
                # If requests.get fails, it will return readable error
                if response.status_code >= 400:
                    raise Exception(
                        f"received status code {response.status_code} from {url}"
                    )
                pbar = tqdm(
                    miniters=1,
                    desc=desc,
                    total=int(response.headers.get("content-length", 0)),
                )
                for chunk in response.iter_content(chunk_size=chunk_size):
                    yield chunk
                    pbar.update(len(chunk))
                pbar.close()
        except ConnectionError:
            raise Exception(f"Failed to read dataset at {url}") from None


async def download(url, path=None, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Downloads file located at URL to path
    :raises: FileNotFoundError if path is invalid.
    :returns: str of PosixPath file was saved to.
    """
    filename = Path(urlparse(url).path).name
    if path is None:
        path = filename
    else:
        path = Path(path)
        if path.is_dir():
            path /= filename
    with open(path, "wb") as f:  # Will raise FileNotFoundError if invalid path
        async for chunk in _get_chunks(url, chunk_size):
            f.write(chunk)
    return str(path)


async def read(url, chunk_size=DEFAULT_CHUNK_SIZE):
    return b"".join([chunk async for chunk in _get_chunks(url, chunk_size)])


def _verify_files_dont_exist(paths):
    for path in paths:
        if Path(path).exists():
            raise FileExistsError(f"Error: File {path} already exists.")


async def prepare(url, path=None):
    """
    prepares a dataset for learners. Downloads a dataset from the given url,
    decompresses it if necessary, and symlinks it so it's available in the desired path
    :param url: the URL to download the dataset from
    :param path: the path the dataset will be available at
    :returns:
    :raises InvalidURLException: it raises this when...
    :raises FileExistsError: it raises this when ...
    :raises ValueError: When requested path is in /tmp
    """

    filename = Path(urlparse(url).path).name
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)
        if path.is_dir():
            path /= Path(urlparse(url).path).stem
    # Check if path contains /tmp
    if Path("/tmp") in path.parents:
        # Is throw error the right thing?
        raise ValueError("path must not be in /tmp")
    # Create the target path if it doesn't exist yet
    path.mkdir(parents=True, exist_ok=True)

    # For avoiding collisions with any other files the user may have downloaded to /tmp/
    tmp_extract_dir = Path(f"/tmp/skills-network-{hash(url)}")
    tmp_download_file = Path(f"/tmp/{tmp_extract_dir.name}-{filename}")
    # Download the dataset to tmp_download_file file
    # File will be overwritten if it already exists
    await download(url, tmp_download_file)

    # Delete tmp_extract_dir directory if it already exists
    if tmp_extract_dir.is_dir():
        shutil.rmtree(tmp_extract_dir)

    # Create tmp_extract_dir
    tmp_extract_dir.mkdir()

    if tarfile.is_tarfile(tmp_download_file):
        with tarfile.open(tmp_download_file) as tf:
            _verify_files_dont_exist(
                [path / name for name in tf.getnames() if len(Path(name).parents) == 1]
            )  # Only check if top-level fileobject
            pbar = tqdm(iterable=tf.getmembers(), total=len(tf.getmembers()))
            pbar.set_description(f"Extracting {filename}")
            for member in pbar:
                tf.extract(member=member, path=tmp_extract_dir)
        tmp_download_file.unlink()
    elif zipfile.is_zipfile(tmp_download_file):
        with zipfile.ZipFile(tmp_download_file) as zf:
            _verify_files_dont_exist(
                [path / name for name in zf.namelist() if len(Path(name).parents) == 1]
            )
            pbar = tqdm(iterable=zf.infolist(), total=len(zf.infolist()))
            pbar.set_description(f"Extracting {tmp_extract_dir}")
            for member in pbar:
                zf.extract(member=member, path=tmp_extract_dir)
        tmp_download_file.unlink()
    else:
        pass  # Anything to do here?

    symlinkme_to_target = {
        path / child.name: child
        for child in tmp_extract_dir.iterdir()
        if not child.name.startswith("._")
    }

    # Now symlink the symlinkmes to targets
    for symlinkme, target in symlinkme_to_target.items():
        symlinkme.symlink_to(target, target_is_directory=target.is_dir())

    return str(path)


if is_jupyterlite():
    tqdm.monitor_interval = 0

# For backwards compatibility
download_dataset = download
read_dataset = read
prepare_dataset = prepare
