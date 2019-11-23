# third party
import pandas as pd
from tqdm import tqdm
from spacy.tokens import Doc

# local
from src.config_ import PATHS
from src.lexisnexis_parser import codify_batch

Doc.set_extension('id', default=None)


def fetch_docs(path, vocab):
    l = len(list(path.glob('*.spacy')))
    for doc in tqdm(
        path.glob('*.spacy'), desc=f"{path.name:.<24}", ncols=120, total=l
        ):
        with open(doc, 'rb') as f:
            yield Doc(vocab).from_bytes(f.read())


def fetch_doc(path, vocab):
    with open(path, 'rb') as f:
        return Doc(vocab).from_bytes(f.read())


def serialize_batch(
    nlp,
    batch,
    path_in=PATHS.data_int,
    path_out=PATHS.data_prc
):
    """
    Add linguistic annotations to a batch of documents with spaCy.
    Then serialize them.

    Documents are loaded from the 'body_str' column of a pickled `DataFrame`.

    Parameters
    ==========
    :param nlp: spaCy model
    :param batch: `str`
        Label used to refer to the set of documents to be processed.

    Optional key-word arguments
    ===========================
    :param path_in: `str` or `Path`
        Path where the batch is stored as pickled `DataFrame`.
    :param path_out: `str` or `Path`
        Path where the serialized `Docs` will be stored.
        They will be collected within their own folder named after the batch.

    Returns
    =======
    :serialize_batch: None
    """

    if isinstance(path_in, str):
        path_in = Path(path_in)
    if isinstance(path_out, str):
        path_out = Path(path_out)

    path_batch = path_out / batch
    if not path_batch.exists():
        path_batch.mkdir(parents=True)

    for doc_file in path_batch.glob('*.spacy'):
        doc_file.unlink()

    df = pd.read_pickle(path_in / f"{batch}_.pkl")
    for idx, body in tqdm(
        df.body_str.iteritems(), desc=f"{batch:.<24}", total=len(df), ncols=80
        ):
        doc_id = f"{codify_batch(batch)}_{idx:04d}"
        doc = nlp(body)
        doc._.id = doc_id
        doc_bytes = doc.to_bytes()
        with open(path_batch / f"{doc_id}.spacy", 'wb') as f:
            f.write(doc_bytes)

    return None
