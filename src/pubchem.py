import pubchempy as pcp
import requests as r
from typing import Any, List, Dict, Tuple
from utils import create_session
import base64


PROPERTIES: List[str] = ["iupac_name", "cid", "elements", "molecular_weight", "molecular_formula"]
PUBCHEM_COMPOUND_URL: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"


def get_structure_img(cid: int, session: r.Session) -> str:
    """Get image of the structure of a chemical entity by cid from PubChem database.

    Args:
        cid (str): PubChem Identifier for chemical
        session (r.Session): requests.Session object for the GET request

    Returns:
        str: Base64 encoded string of the image
    """
    try:
        response = session.get(url=f"{PUBCHEM_COMPOUND_URL}{str(cid)}/PNG")
        img = str(base64.b64encode(response.content))[3:-1]
    except:
        return None
    return img


def search_pubchem(
    search_term: str, session: r.Session, num_results_used: int = 1
) -> List[Tuple[List[str], Dict[str, Any], str]]:
    """Search PubChem with search term and extract chemical properties (specified
       in PROPERTIES), specified number of relavant synonyms and the 2D structure of the compounds found.

    Args:
        search_term (str): Search term to use for searching PubChem database
        session (r.Session): requests.Session object for the GET request
        num_results_used (int, optional): Number of search results to consider. Defaults to 1.

    Returns:
        List[Tuple[List[str], Dict[str, Any], str]]: List of compounds, each element consisting of: (snyonyms, properties, image)
    """
    compound_list: List[Tuple[List[str], Dict[str, Any], str]] = []
    search_results = pcp.get_compounds(search_term, "name")[0:num_results_used]
    if not search_results:
        try:
            search_results = pcp.get_compounds(search_term, "formula")[0:num_results_used]
        except:
            pass
    for compound in search_results:
        properties: Dict[(str, Any)] = compound.to_dict(properties=PROPERTIES)
        synonyms: List[str] = compound.synonyms[0:5]
        structure_img: str = get_structure_img(properties["cid"], session)
        compound_list.append((synonyms, properties, structure_img))
    return compound_list


if __name__ == "__main__":
    s = create_session()
    compound = search_pubchem("water", s)
