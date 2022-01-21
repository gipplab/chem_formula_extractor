from hyplag_backend import *
from parser import clean_xml, TeiXmlReader
from pubchem import *
import logging
import json


def process_pdf(pdf_name: str):
    if os.path.exists("grobid_config.json"):
        try:
            process_documents_grobid(Path(PDF_FILES + pdf_name))
        except ConnectionRefusedError:
            logging.warning("Grobid Docker Container is not running.")
    else:
        token = get_current_token()
        document_id = post_document(PDF_FILES + pdf_name, token)
        document = get_document(document_id, token)
        save_xml_doc(Path(pdf_name[:-4] + ".xml"), document)
    xml_name = ""
    xml_root = clean_xml(xml_name)
    cde_document = TeiXmlReader().parse(xml_root)
