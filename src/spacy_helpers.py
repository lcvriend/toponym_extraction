import pandas as pd
from spacy.tokens import Doc
from .config import PATH_DATA_I, PATH_DATA_P
from .lexisnexis_parser import codify_batch
Doc.set_extension('id', default=None)


def fetch_docs(path, vocab):
    for doc in path.glob('*.spacy'):
        with open(doc, 'rb') as f:
            yield Doc(vocab).from_bytes(f.read())


def serialize_batch(nlp, batch, path_in=PATH_DATA_I, path_out=PATH_DATA_P):
    """
    Add linguistic annotations to a batch of documents with spaCy.
    Then serialize them.

    The documents are loaded from the 'body_' column of a pickled `DataFrame`.

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

    print(f"Processing: {batch}")
    df = pd.read_pickle(path_in / f"{batch}_.pkl")
    for idx, body in df.body_.iteritems():
        doc_id = f"{codify_batch(batch)}_{idx:03d}"
        doc = nlp(body)
        doc._.id = doc_id
        doc_bytes = doc.to_bytes()
        with open(path_batch / f"{doc_id}.spacy", 'wb') as f:
            f.write(doc_bytes)

    return None
