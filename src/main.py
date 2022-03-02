from hyplag_backend import (
    process_documents_grobid,
    get_current_token,
    post_document,
    get_document,
    save_xml_doc,
)
from parser import clean_xml, TeiXmlReader
from pubchem import search_pubchem
from pathlib import Path
from definitions import PDF_FILES
from utils import create_session


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
    session = create_session()
    cid_list = []
    for chem in cde_document.records.serialize():
        chemical = []
        # Extracted chemical compounds
        compound = chem.get("Compound")
        if compound:
            chem_names = compound.get("names")
            if not chem_names:
                continue
        else:
            continue

        for name in chem_names:
            # Further information from pubchem
            temp_name = name.replace(".", ",")
            temp_name = temp_name.replace(" ", "")
            compound_properties = search_pubchem(temp_name, session)
            if compound_properties:
                compound_properties[0][1]["elements"] = list(
                    set(compound_properties[0][1]["elements"])
                )
                iupac_name = compound_properties[0][1]["iupac_name"]
                if iupac_name:
                    compound_properties[0][1]["iupac_name"] = iupac_name.replace(";", " ")
                cid = compound_properties[0][1]["cid"]
                if cid in cid_list:
                    continue
                cid_list.append(cid)
                chemical.extend(list(compound_properties[0][1].values()))
                chemical.append(compound_properties[0][2])
            else:
                continue
        if chemical:
            chemical_list.append(chemical)
    return chemical_list


if __name__ == "__main__":
    chem_list = process_pdf("acssuschemeng.7b03870.pdf")
