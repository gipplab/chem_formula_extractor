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
from typing import List, Any


CID_INDEX: int = 1

def process_pdf(pdf_name: str) -> List[Any]:
    """Processes the input pdf file and extracts all chemical entities.

    Args:
        pdf_name (str): Name of the pdf file in PDF_FILES folder

    Returns:
        List[List[Any]]: List of chemical entities. Each element consists of:
                         [Iupac name, CID, List of Atoms, Molecule Weight, Molecular Formula, 
                          Base64 encoded image of molecular structure]
    """
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
            temp_name = name
            compound_properties = search_pubchem(temp_name, session)
            if not compound_properties and "." in temp_name:
                compound_properties = search_pubchem(temp_name.replace(".", ","), session)
            if not compound_properties and " " in temp_name:
                compound_properties = search_pubchem(temp_name.replace(" ", ""), session)

            if compound_properties:
                # If chemical is already extracted skip it
                cid = compound_properties[0][1]["cid"]
                if cid in cid_list:
                    continue
                # Set of elements
                compound_properties[0][1]["elements"] = list(
                    set(compound_properties[0][1]["elements"])
                )
                # Name 
                iupac_name = compound_properties[0][1]["iupac_name"]
                if iupac_name:
                    compound_properties[0][1]["iupac_name"] = iupac_name.replace(";", " ")
                cid_list.append(cid)
                chemical.extend(list(compound_properties[0][1].values()))
                # Use extracted name if no iupac name avaiable
                if compound_properties[0][1]["iupac_name"] is None:
                    chemical[0] = name
                chemical.append(compound_properties[0][2])
            else:
                # If no results form pubchem, skip the chemical entity
                continue
            if chemical:
                chemical_list.append(chemical)
    return chemical_list

def compare_documents(source_pdf: str, recommendation_pdf: str) -> List[List[Any]]:
    """Compares chemical entities of two scientific papers. Returns
    their chemical entities and the indexes of same entities.

    Args:
        source_pdf (str): Source pdf file of comparison
        recommendation_pdf (str): Target pdf of for comparison

    Returns:
        List[List[Any]]: [Chemical entities of source document, Chemical entities of target document,
                          Index pairs for same entities [i, j]]
    """
    index_list: List[List[int]] = []
    source_chemical_list = process_pdf(source_pdf)
    recommendation_chemical_list = process_pdf(recommendation_pdf)
    for i, source_chemical in enumerate(source_chemical_list):
        for j, recommendation_chemical in enumerate(recommendation_chemical_list):
            if source_chemical[CID_INDEX] == recommendation_chemical[CID_INDEX]:
                index_list.append([i, j])
                break
    return source_chemical_list, recommendation_chemical_list, index_list


if __name__ == "__main__":
    chem_list = process_pdf("acssuschemeng.7b03870.pdf")
