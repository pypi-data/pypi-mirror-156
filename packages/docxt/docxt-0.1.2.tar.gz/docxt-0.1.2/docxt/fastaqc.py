import re
from bs4 import BeautifulSoup

try:
    from .utils.html import parse_table
except ImportError:
    from utils.html import parse_table


class FastaqcHTML:

    def __init__(self, html_path: str) -> None:
        self.html_path = html_path

        with open(html_path) as r:
            html = BeautifulSoup(r, "html.parser")

        divs = list(html.body.children)
        self.header = divs[0]
        self.summary = divs[1]
        self.main = divs[2]
        self.footer = divs[3]

        self.modules = {}
        for m in self.main.children:
            md = {}
            md['id'] = m.h2.attrs['id']
            md['title'] = m.h2.text
            md['el'] = m.h2.next_sibling
            self.modules[md['id']] = md

        self.__cached__ = {"fastaqc_version": None, "basic_statistics": None}

    @property
    def basic_statistics(self):
        if self.__cached__["basic_statistics"] is None:
            rows = parse_table(self.modules['M0']['el'])
            self.__cached__["basic_statistics"] = rows
        return self.__cached__["basic_statistics"]

    @property
    def fastaqc_version(self):
        if self.fastaqc_version is None:
            res = re.search(r'\(version (.*?)\)', str(self.footer))
            self.__cached__["fastaqc_version"] = res.groups()[0]
        return self.__cached__["fastaqc_version"]


def get_basic_statistics(html_path: str):

    with open(html_path) as r:
        html = BeautifulSoup(r, "html.parser")
    divs = list(html.body.children)
    main_box = divs[2]

    modules = {}
    for m in main_box.children:
        md = {}
        md['id'] = m.h2.attrs['id']
        md['title'] = m.h2.text
        md['el'] = m.h2.next_sibling
        modules[md['id']] = md

    rows = parse_table(modules['M0']['el'])
    qc = {d['Measure']: d['Value'] for d in rows}
    return qc


if __name__ == '__main__':

    html = "/home/barwe/projects/pathogen/output_dir/task_20210309172157/QC/1_2P.trim_fastqc.html"
    # qc = FastaqcHTML(html)
    print(get_basic_statistics(html))
