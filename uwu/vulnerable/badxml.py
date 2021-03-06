import xml.sax
import zipfile


class XLSXCoreHandler(xml.sax.ContentHandler):
    def __init__(self, result_dict):
        self.res = result_dict
        xml.sax.ContentHandler.__init__(self)

    def startElement(self, name, attrs):
        self.tmp = ''

    def endElement(self, name):
        if name == "dc:creator":
            self.res['creator'] = self.tmp
        elif name == 'cp:lastModifiedBy':
            self.res['lastModifiedBy'] = self.tmp
        elif name == 'dcterms:modified':
            self.res['modified'] = self.tmp
        elif name == 'dcterms:created':
            self.res['created'] = self.tmp

    def characters(self, content):
        self.tmp += content


class XLSXWorkbookHandler(xml.sax.ContentHandler):
    def __init__(self, result_dict):
        self.res = result_dict
        xml.sax.ContentHandler.__init__(self)
        self.tmp = ''
        self.tmpattrs = None

    def startElement(self, name, attrs):
        self.tmp = ''
        if name == 'sheet':
            self.tmp = attrs.getValue('name')

    def endElement(self, name):
        if name == 'sheet':
            self.res['name'] = self.tmp

    def characters(self, content):
        self.tmp += content


def xlsx_attributes(f):
    '''
    Get the title, creator, creation and modification times, and last
    modifying author for an XLSX `f`. `f` should be a file object to an
    XLSX file.
    '''
    z = zipfile.ZipFile(f)
    props = {}
    with z.open('docProps/core.xml') as f:
        xml.sax.parse(f, XLSXCoreHandler(props))
    with z.open('xl/workbook.xml') as f:
        xml.sax.parse(f, XLSXWorkbookHandler(props))
    return props
