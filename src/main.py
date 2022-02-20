from hyplag_backend import *
from parser import clean_xml, TeiXmlReader
from pubchem import search_pubchem


def process_pdf(pdf_name: str):
    try:
        process_documents_grobid(Path(PDF_FILES + pdf_name))
    except:
        token = get_current_token()
        document_id = post_document(Path(PDF_FILES + pdf_name), token)
        document = get_document(document_id, token)
        save_xml_doc(Path(pdf_name[:-4] + ".xml"), document)
    xml_name = pdf_name[:-4] + ".xml"
    xml_root = clean_xml(xml_name)
    cde_document = TeiXmlReader().parse(xml_root)
    chemical_list = []
    for chem in cde_document.records:
        chemical = []
        cid_list = []
        # Extracted chemical compounds
        chem_names = chem.serialize()
        chemical.append(chem_names)
        for name in chem_names:
            # Further information from pubchem
            compound = search_pubchem(name)
            cid = compound[1][0]
            if cid in cid_list:
                continue
            cid_list.apppend(cid)
            for item in compound:
                chemical.append(item)
        chemical_list.append(chemical)
    return chemical_list


if __name__ == "__main__":
    chem_list = process_pdf("acssuschemeng.7b03870.pdf")
