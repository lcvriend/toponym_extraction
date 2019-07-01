#standard library
import requests
from pathlib import Path

# third party
from tqdm import tqdm


def download_from_url(url, path_out=None):
    file_path = Path(url).name
    r = requests.get(url, stream=True)
    size = r.headers['Content-length']

    if not r.status_code == requests.codes.ok:
        raise requests.exceptions.HTTPError(
            f"The following url: '{url}' returned status code {r.status_code}. "
            f"Check if the provided url is still valid."
            )
    if path_out:
        file_path = path_out / file_path
    with open(file_path, 'wb') as handle:
        iter_bytes = tqdm(
            r.iter_content(),
            desc=f"{file_path.name:.<24}",
            total=int(size),
            )
        for data in iter_bytes:
            handle.write(data)
    return None
