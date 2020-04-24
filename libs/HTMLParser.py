from bs4 import BeautifulSoup
from core.models.Table import Table


class HtmlParser(object):
    """
    Class to support parse html content
    """

    # ----------------- Private methods -------------------
    def __init__(self):
        self.__raw__ = None

    # ----------------- Public methods -------------------
    def get_childs(self, tagname):
        """
        Return a list of child element base on expected tagname
        @param tagname: tagname to get
        @return: list of childs
        """
        return self.__raw__.findAll(tagname)

    def parse_table(self):
        """
        Parse a table from htmlparser object
        @return: a list dict virtualize the parsed table
        """
        # Parse header
        tmp_header = []
        for elem in self.__raw__.findAll('th'):
            tmp_header.append(''.join([str(s) for s in elem.findAll(text=True)]))

        # Parse content
        tmp_table = []
        for row in self.__raw__.findAll('tr'):
            tmp_row = []
            for cell in row.findAll('td'):
                tmp_cell_val = ''.join([str(s) for s in cell.findAll(text=True)])
                tmp_row.append(tmp_cell_val)
            if tmp_row:
                tmp_table.append(tmp_row)
        return Table(tmp_table, columns=tmp_header)

    @staticmethod
    def get_html_file_content(filepath):
        """
        Return a htmlParser object which holds html content from a html or text file
        @param filepath: path to html file
        @return: self
        """
        with open(filepath) as fp:
            return HtmlParser.get_html_content(fp)

    @staticmethod
    def get_html_content(text):
        """
        Return a htmlParser object from a block of html text
        @param text: block of html content to format
        @return: self
        """
        new_iParser = HtmlParser()
        new_iParser.__raw__ = BeautifulSoup(text, 'html.parser')
        return new_iParser
