from xml.etree.ElementTree import ElementTree
from lxml import etree
from definitions import XML_FILES
from typing import List
import logging
from collections import defaultdict
from chemdataextractor.doc import Document, Table, Figure, Heading, Caption, Title
from chemdataextractor.scrape.clean import Cleaner
from chemdataextractor.reader.markup import LxmlReader
from chemdataextractor.doc.meta import MetaData
from chemdataextractor.errors import ReaderError
from chemdataextractor.model import Compound
from lxml.etree import XMLParser

NAMESPACE: str = "{http://www.tei-c.org/ns/1.0}"


def clean_xml(xml_file: str) -> etree.ElementTree:
    """Cleans the xml file from namespace urls

    Args:
        xml_file (str): XML file in directory XML_FILES

    Returns:
        etree.ElementTree: Opened xml file with remove namespace urls 
    """
    with open(XML_FILES + xml_file, "rb") as file:
        xml_doc = file.read()
        xml_tree = etree.fromstring(xml_doc)

    # Remove the namespace url from element name
    for elem in xml_tree.iter():
        try:
            elem.tag = etree.QName(elem).localname
        except ValueError:
            logging.warning(f"Element {elem.tag} has no name.")
    etree.cleanup_namespaces(xml_tree)

    return xml_tree


class TeiXmlReader(LxmlReader):
    """Reader for xml files, which follow the TEI standard (grobid, hyplag).

    Args:
        LxmlReader : _description_

    Raises:
        ReaderError: _description_

    Returns:
        _type_: _description_
    """
    # Xpath expressions for different document elements
    main_document_body = ".//body"

    metadata_xpath = "//fileDesc"
    metadata_title_xpath = ".//titleStmt/title"
    metadata_date_xpath = ".//publicationStmt/date"
    metadata_doi_xpath = ".//idno[@type='DOI']"
    metadata_authors_xpath = ".//author/persName"

    headings_xpath = ".//div/head"

    figures_xpath = "//div//*//figure[contains(@xml:id, 'fig')]"
    figures_caption_xpath = "figDesc"
    figures_label_xpath = "label"

    tables_xpath = "//div//*//figure[contains(@xml:id, 'tab')]"
    table_rows_xpath = "table/row"
    tables_caption_xpath = "figDesc"
    tables_label_xpath = "label"

    references_text_xpath = "//div//*//ref[contains(@target, '#b')]"
    references_bibliography_xpath = "//bibleStruct"
    # Cleaner for removing references without proper id
    cleaner = Cleaner(kill_xpath="//div//*//ref[contains(@target, '#b')]")

    def _parse_reference(self, el) -> int:
        """Parse reference id.

        Args:
            el (xml element): Reference xml element, for example <ref type="bibr" target="#b0">

        Returns:
            int: Bibliography number
        """
        bib_id: str = el.get("target")
        if bib_id:
            # Remove #b
            bib_id = [int(bib_id[2:])]
            return bib_id
        return 1000

    def _parse_figure(self, el, refs, specials) -> List[Figure]:
        """Parse a figure to a CDE figure object.

        Args:
            el (xml element): Root xml element
            refs : References, which are child elements of el
            specials (dict): Dictionary of already created object

        Returns:
            List[Figure]: [CDE figure object]
        """
        caps = self._xpath(self.figures_caption_xpath, el)
        label = self._xpath(self.figures_label_xpath, el)
        caption = (
            self._parse_text(caps[0], refs=refs, specials=specials, element_cls=Caption)[0]
            if caps
            else Caption("")
        )
        figure = Figure(caption, label=label, links=None)
        return [figure]

    def _parse_table_rows(self, els, refs, specials):
        hdict = {}

    def _parse_table(self, el, refs, specials) -> List[Table]:
        """Parse a table to a CDE table object.

        Args:
            el (xml element): Root xml element
            refs : References, which are child elements of el
            specials (dict): Dictionary of already created objects

        Returns:
            List[Table]: [CDE table object]
        """
        caps = self._xpath(self.figures_caption_xpath, el)
        caption = (
            self._parse_text(caps[0], refs=refs, specials=specials, element_cls=Caption)[0]
            if caps
            else Caption("")
        )
        table = Table(caption, table_data=None)
        return [table]

    def _parse_authors(self, el) -> List[str]:
        """Parse the xml element, which contains the authors, into a list of author names

        Args:
            el (xml element): Root xml element
        Returns:
            List[str]: List of author names
        """
        author_list = []
        for author in self._xpath(self.metadata_authors_xpath, el):
            name = ""
            for i in author.iter():
                if i.text is not None:
                    name += i.text + " "
            name = name[:-1]
            author_list.append(name)
        return author_list

    def _parse_metadata(self, el) -> List[MetaData]:
        """Parses the medata of xml element into CDE Metadata object.

        Args:
            el (xml element): Root xml element

        Returns:
            List[MetaData]: [Metadataobject]
        """
        title = self._xpath(self.metadata_title_xpath, el)
        authors = self._parse_authors(el)
        publisher = None
        journal = None
        date = self._xpath(self.metadata_date_xpath, el)
        language = None
        volume = None
        issue = None
        firstpage = None
        lastpage = None
        doi = self._xpath(self.metadata_doi_xpath, el)
        pdf_url = None
        html_url = None

        metadata = {
            "_title": title[0] if title else None,
            "_authors": authors if authors else None,
            "_publisher": publisher[0] if publisher else None,
            "_journal": journal[0] if journal else None,
            "_date": date[0] if date else None,
            "_language": language[0] if language else None,
            "_volume": volume[0] if volume else None,
            "_issue": issue[0] if issue else None,
            "_firstpage": firstpage[0] if firstpage else None,
            "_lastpage": lastpage[0] if lastpage else None,
            "_doi": doi[0] if doi else None,
            "_pdf_url": pdf_url[0] if pdf_url else None,
            "_html_url": html_url[0] if html_url else None,
        }
        meta = MetaData(metadata)
        return [meta]

    def _make_tree(self, fstring: str) -> ElementTree:
        """Create xml tree from string

        Args:
            fstring (str): XML string

        Returns:
            ElementTree: XML tree
        """
        root = etree.fromstring(fstring, parser=XMLParser(recover=True))
        return root

    def parse(self, file) -> Document:
        """Parse a xml file into a CDE document

        Args:
            file: XML string

        Raises:
            ReaderError: XML could not be read

        Returns:
            Document: CDE document
        """
        if type(file) == etree._Element:
            root = file
        else:
            root = self._make_tree(file)

        self.root = root

        if root is None:
            raise ReaderError
        for cleaner in self.cleaners:
            cleaner(root)
        specials = {}
        refs = defaultdict(list)
        titles = self._xpath(self.metadata_title_xpath, root)
        headings = self._xpath(self.headings_xpath, root)
        figures = self._xpath(self.figures_xpath, root)
        tables = self._xpath(self.tables_xpath, root)
        # citations = self._css(self.citation_css, root)
        references = self._xpath(self.references_text_xpath, root)
        # ignores = self._css(self.ignore_css, root)
        md = self._xpath(self.metadata_xpath, root)
        for reference in references:
            refs[reference.getparent()].extend(self._parse_reference(reference))
        # for ignore in ignores:
        #    specials[ignore] = []
        for title in titles:
            specials[title] = self._parse_text(
                title, element_cls=Title, refs=refs, specials=specials
            )
        for heading in headings:
            specials[heading] = self._parse_text(
                heading, element_cls=Heading, refs=refs, specials=specials
            )
        for figure in figures:
            specials[figure] = self._parse_figure(figure, refs=refs, specials=specials)
        for table in tables:
            specials[table] = self._parse_table(table, refs=refs, specials=specials)
        # for citation in citations:
        #    specials[citation] = self._parse_text(citation, element_cls=Citation, refs=refs, specials=specials)
        specials[md[0]] = self._parse_metadata(root)
        root = self.root.find(self.main_document_body)
        elements = self._parse_element(root, specials=specials, refs=refs)
        return Document(*elements, models=[Compound])


if __name__ == "__main__":
    root = clean_xml("acssuschemeng.7b03870.tei.xml")
    hans = root.find(".//body")
    print("test")
