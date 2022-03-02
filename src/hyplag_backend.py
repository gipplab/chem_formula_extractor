import os
import requests
from typing import Dict, List, Tuple
from pathlib import Path
from definitions import (TOKEN, HYPLAG_USER, HYPLAG_PASSWORD, HYPLAG_BACKEND_AUTH_TOKEN, HYPLAG_ID, 
                        HYPLAG_BACKEND_POST_DOCUMENT, HYPLAG_BACKEND_GET_DOCUMENT, XML_FILES, 
                        PDF_FILES)
from glob import glob
from datetime import datetime, timedelta
from grobid_client.grobid_client import GrobidClient
import concurrent.futures


def get_current_token() -> str:
    if os.path.exists(TOKEN):
        with open(TOKEN, "w+") as file:
            token_time: str = file.readline()[:-1]
            if token_time:
                token_time = datetime.strptime(token_time, "%Y-%m-%d %H:%M:%S.%f")
                old_token: str = file.readline()
                current_time = datetime.utcnow()
                time_diff = current_time - token_time
                if time_diff < timedelta(hours=2):
                    token = old_token
                else:
                    token, token_time = get_auth_token()
            else:
                token, token_time = get_auth_token()
            file.writelines([str(token_time) + "\n", token])
    else:
        with open(TOKEN, "x") as file:
            token, token_time = get_auth_token()
            file.writelines([str(token_time) + "\n", token])
    return token


def get_auth_token(
    username: str = HYPLAG_USER, password: str = HYPLAG_PASSWORD
) -> Tuple[str, str]:
    token_time = str(datetime.utcnow())
    headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    payload: str = f'{{"name": "{username}",                        "password": "{password}"}}'
    response = requests.post(url=HYPLAG_BACKEND_AUTH_TOKEN, data=payload, headers=headers)
    return response.json()["token"], token_time


def post_document(path_to_document: Path, token: str, external_id: str = HYPLAG_ID) -> int:
    headers: Dict = {"Authorization": f"Bearer {token}"}
    files = {
        "external_id": (None, f"{external_id}"),
        "multipartFile": (path_to_document.name, open(path_to_document, "rb")),
    }
    response = requests.post(url=HYPLAG_BACKEND_POST_DOCUMENT, headers=headers, files=files)
    return response.json()


def post_documents_from_list(
    list_of_documents: List[Path], token: str, external_id: str = HYPLAG_ID, num_threads: int = 10
) -> List[int]:
    document_id_list = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(num_threads, len(list_of_documents))
    ) as executor:
        doc_ids = [
            executor.submit(post_document, str(path), token, external_id)
            for path in list_of_documents
        ]
        for doc_id in concurrent.futures.as_completed(doc_ids):
            document_id_list.append(doc_id.result())
    return document_id_list


def post_documents_from_folder(
    folder: Path, token: str, external_id: str = HYPLAG_ID
) -> List[int]:
    documents = glob(str(folder) + "/*.pdf")
    document_id_list = post_documents_from_list(documents, token, external_id)
    return document_id_list


def get_document(document_id: int, token: str):
    get_url = HYPLAG_BACKEND_GET_DOCUMENT + str(document_id) + "/tei"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = requests.get(url=get_url, headers=headers)
    return response.text


def get_documents_from_list(list_document_ids: List[int], token: str, num_threads: int):
    assert num_threads >= 1, "Number of threads has to be equal or greater than 1."
    xml_document_list = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(num_threads, len(list_document_ids))
    ) as executor:
        paper_xml_download = [
            executor.submit(get_document, doc_id, token) for doc_id in list_document_ids
        ]
        for xml in concurrent.futures.as_completed(paper_xml_download):
            xml_document_list.append(xml.result())
    return xml_document_list


def save_xml_doc(path_to_save: Path, xml_doc: str):
    with open(XML_FILES + str(path_to_save), "w") as file:
        file.write(xml_doc)


def process_documents_grobid(path_to_pdf: Path = Path(PDF_FILES), num_threads: int = 10):
    client = GrobidClient(config_path="./grobid_config.json")
    client.process(
        service="processFulltextDocument",
        input_path=str(path_to_pdf),
        output=str(XML_FILES),
        n=num_threads,
        consolidate_header=False,
    )


if __name__ == "__main__":
    # token = get_current_token()
    # doc_id = post_document(Path(PDF_FILES + "acssuschemeng.7b03870.pdf"), token)
    # doc = get_document(doc_id, token)
    # save_xml_doc(path_to_save=Path("test2.xml"), xml_doc=doc)
    process_documents_grobid()
