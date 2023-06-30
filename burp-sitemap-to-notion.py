from burp import IBurpExtender, IHttpListener, ITab
import csv
from javax import swing
from javax.swing import JFileChooser
from javax.swing import JTable
from javax.swing.table import DefaultTableModel
from javax.swing.filechooser import FileNameExtensionFilter
from javax.swing import JOptionPane
from java.awt import Color
from java.awt import Font
import java.lang as lang

import json
import urllib2

BASE_URL = "https://api.notion.com/%s"
TOKEN="secret_V2PSktPqOfODZHDJemXZqGlVee3ozH6EFgCdEC1Ojo1"

class NotionWrapper():
    def __init__(self, token, base_url="https://api.notion.com/%s"):
        self.database_id = None
        self.BASE_URL = base_url
        self.TOKEN = token

    def do_api_request(self, endpoint, body):
        body = json.dumps(body)
        body = body.encode()
        endpoint = endpoint.encode() # need this line because of this: https://github.com/coinbase/coinbase-python/issues/10
        req = urllib2.Request(self.BASE_URL % endpoint, body)
        req.add_header("Authorization", "Bearer " + self.TOKEN)
        req.add_header("Content-Type", "application/json")
        req.add_header("Notion-Version", "2022-06-28")
        print(req.get_full_url())
        resp = urllib2.urlopen(req)
        return json.loads(resp.read())

    def get_pages(self, name=""):
        """
            A funciton to get the pages a name can be specified but if no name give it will get all of the pages available
        """
        body = {
            "query": name,
             "filter": {
              "value": "page",
              "property": "object"
            }
        }
        json_data = self.do_api_request('v1/search', body)
        self.first_id = json_data["results"][0]["id"] 
        return json_data["results"]

    def get_database_entries(self, db_id):
        """
            A funciton to get the pages a name can be specified but if no name give it will get all of the pages available
        """
        body = {}
        json_data = self.do_api_request('v1/databases/%s/query' % db_id, body)
        return json_data["results"]

    def create_page_from_template(self, parent_id, title):
        body = {
            "parent": {
                "database_id": parent_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "Not Tested"
                    }
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{ "type": "text", "text": { "content": "Endpoints:" } }]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{ "type": "text", "text": { "content": "Scans:" } }]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "caption": [],
                        "rich_text": [{ "type": "text", "text": { "content": "...." } }],
                        "language": "bash"
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{ "type": "text", "text": { "content": "Screenshots:" } }]
                    }
                }
            ]
        }
        json_data = self.do_api_request('v1/pages', body)
        print(json_data)
        return json_data["id"]

    def create_database_from_template(self, parent_id):
        body = {
            "parent": {
                "type": "page_id",
                "page_id": self.first_id
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "Site Map"
                    }
                }
            ],
            "properties": {
                "Name": {
                    "title": {}
                },
                "Status": {
                    "select": {
                        "options": [
                            {
                                "name": "Not Tested",
                                "color": "gray"
                            },
                            {
                                "name": "Testing",
                                "color": "orange"
                            },
                            {
                                "name": "NOT Vulnerable",
                                "color": "green"
                            },
                            {
                                "name": "Vulnerable",
                                "color": "red"
                            }
                        ]
                    }
                }
            }
        }
        json_data = self.do_api_request('v1/databases', body)
        return json_data["id"]

class BurpExtender(IBurpExtender, IHttpListener, ITab):
    def registerExtenderCallbacks(self, callbacks):
        self.nw = NotionWrapper(token=TOKEN)
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.colName = [ 'Method', 'status', 'path' ]
        self.bigest_length = 0
        self.csv_data = []
        self.drawUI()
        callbacks.registerHttpListener(self)
        callbacks.addSuiteTab(self)
        callbacks.setExtensionName("SiteMap To Notion")
        self.nw.get_pages()
        idnum = self.nw.create_database_from_template("replace_with_id")
        self.nw.create_page_from_template(idnum, '/')
        print(self.nw.get_database_entries(idnum))

    def drawUI(self):
        self.tab = swing.JPanel()
        # This part is just for the export button
        self.uiExportRun = swing.JButton('Export',actionPerformed=self.exportAndSaveCsv)
        # This part will be for the log panel
        self.uiLogLabel = swing.JLabel('Log:')
        self.uiLogLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiLogPane = swing.JScrollPane()

        # Common UI stuff
        layout = swing.GroupLayout(self.tab)
        self.tab.setLayout(layout)
        # Yes this look awefull thanks to Java
        layout.setHorizontalGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                                  .addGroup(layout.createSequentialGroup()
                                            .addGap(10,10,10)
                                            .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                                                      .addComponent(self.uiExportRun)
                                                        .addGap(15,15,15)
                                                        .addComponent(self.uiLogLabel)
                                                        .addComponent(self.uiLogPane)
                                                    )
                                                .addContainerGap(26, lang.Short.MAX_VALUE)
                                            )
                                  )
        # For some reason you need horizontal and vertical group for it to work :/
        layout.setVerticalGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                                  .addGroup(layout.createSequentialGroup()
                                            .addGap(15,15,15)
                                            .addComponent(self.uiExportRun)
                                            .addGap(20,20,20)
                                            .addComponent(self.uiLogLabel)
                                            .addGap(5,5,5)
                                            .addComponent(self.uiLogPane)
                                            .addGap(5,5,5)
                                            )
                                )

    def getTabCaption(self):
        return 'SiteMap To Notion'

    def getUiComponent(self):
        return self.tab

    def exportAndSaveCsv(self, e):
        f, ok = self.openFile('csv', 'CSV Files', 'wb')
        if ok:
            self.writer = csv.writer(f)
            self.writer.writerow(self.colName)
            for line in self.csv_data:
                self.writer.writerow(line)
            f.close()

    def openFile(self, fileext, filedesc, fileparm):
        myFilePath = ''
        chooseFile = JFileChooser()
        myFilter = FileNameExtensionFilter(filedesc,[fileext])
        chooseFile.setFileFilter(myFilter)
        ret = chooseFile.showOpenDialog(self.tab)
        if ret == JFileChooser.APPROVE_OPTION:
            file = chooseFile.getSelectedFile()
            myFilePath = str(file.getCanonicalPath()).lower()
            if not myFilePath.endswith(fileext):
                myFilePath += '.' + fileext
            okWrite = JOptionPane.YES_OPTION
            if os.path.isfile(myFilePath):
                okWrite = JOptionPane.showConfirmDialog(self.tab,'File already exists. Ok to over-write?','',JOptionPane.YES_NO_OPTION)
                if okWrite == JOptionPane.NO_OPTION:
                    return
            j = True
            while j:
                try:
                    f = open(myFilePath,mode=fileparm)
                    j = False
                except IOError:
                    okWrite = JOptionPane.showConfirmDialog(self.tab,'File cannot be opened. Correct and retry?','',JOptionPane.YES_NO_OPTION)
                    if okWrite == JOptionPane.NO_OPTION:
                        return None, False
            return f, True

    def populate_array(self, status, uri, method):
        data_uri = uri.split('/')[1:]
        if isinstance(data_uri, str) or len(data_uri) == 0:
            return
        data_uri.insert(0, status)
        data_uri.insert(0, method)
        if len(self.csv_data) == 0:
            self.csv_data.append(data_uri)
        else:
            i = 0
            j = 0
            while i < len(self.csv_data) and j < len(data_uri):
                if self.bigest_length < len(data_uri):
                    self.bigest_length = len(data_uri)
                if data_uri in self.csv_data:
                    return
                if j == len(self.csv_data[i]):
                    i = i + 1
                    j = 0
                    continue
                if self.csv_data[i][j] != data_uri[j]:
                    #split array and insert
                    self.csv_data.insert(i, data_uri)
                    break
                else:
                    # elements are equal so go back up
                    j = j + 1
                    continue
        if self.bigest_length > len(self.colName):
            for i in range(len(self.colName), self.bigest_length):
                self.colName.append('path')
        dataModel = DefaultTableModel(self.csv_data, self.colName)
        self.uiLogTable = swing.JTable(dataModel)
        self.uiLogTable.setAutoCreateRowSorter(True);
        self.uiLogPane.setViewportView(self.uiLogTable)

    def getResponseStatus(self, content):
        response = content.getResponse();
        response_data = self._helpers.analyzeResponse(response)
        headers = list(response_data.getHeaders())
        code = headers[0].split(' ')[1]
        return code

    def getRequestUriAndMethod(self, content):
        request = content.getRequest();
        request_data = self._helpers.analyzeRequest(request)
        headers = list(request_data.getHeaders())
        uri = headers[0].split(' ')[1]
        method = headers[0].split(' ')[0]
        return uri, method

    def processHttpMessage(self, tool, is_request, content):
        if is_request:
            return
        uri, method = self.getRequestUriAndMethod(content)
        status = self.getResponseStatus(content)
        if self._callbacks.isInScope(self._helpers.analyzeRequest(content).getUrl()):
            print('saving: %s' % self._helpers.analyzeRequest(content).getUrl())
            self.populate_array(status, uri, method)
