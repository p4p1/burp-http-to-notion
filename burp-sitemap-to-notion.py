from burp import IBurpExtender, IHttpListener, ITab
from javax import swing
from javax.swing import JFileChooser
from javax.swing import JTable
from javax.swing.table import DefaultTableModel
from javax.swing.filechooser import FileNameExtensionFilter
from javax.swing import JOptionPane
from java.awt import Dimension
from java.awt import Color
from java.awt import Font
import java.lang as lang

import json
import urllib2

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
        return json_data["results"]

    def get_database_entries(self, db_id):
        """
            A funciton to get the pages a name can be specified but if no name give it will get all of the pages available
        """
        body = {}
        json_data = self.do_api_request('v1/databases/%s/query' % db_id, body)
        return json_data["results"]

    def create_root_page_from_template(self, parent_id, title):
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
                }
            ]
        }
        json_data = self.do_api_request('v1/pages', body)
        return json_data["id"]

    def create_child_page_from_template(self, parent_id, title, method):
        body = {
            "parent": {
                "database_id": parent_id
            },
            "properties": {
                "Endpoint": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Method": {
                    "select": {
                        "name": method
                    }
                }
            },
            "children": [
            ]
        }
        json_data = self.do_api_request('v1/pages', body)
        return json_data["id"]

    def create_root_database_from_template(self, parent_id, isinline=False):
        body = {
            "parent": {
                "type": "page_id",
                "page_id": parent_id
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "Site Map"
                    }
                }
            ],
            "is_inline": isinline,
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

    def create_inline_database_from_template(self, parent_id, isinline=True):
        body = {
            "parent": {
                "type": "page_id",
                "page_id": parent_id
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "Requests"
                    }
                }
            ],
            "is_inline": isinline,
            "properties": {
                "Method": {
                    "select": {
                        "options": [
                            {
                                "name": "PATCH",
                                "color": "gray"
                            },
                            {
                                "name": "POST",
                                "color": "orange"
                            },
                            {
                                "name": "GET",
                                "color": "green"
                            },
                            {
                                "name": "DELETE",
                                "color": "red"
                            },
                            {
                                "name": "PUT",
                                "color": "blue"
                            }
                        ]
                    }
                },
                "Endpoint": {
                    "title": {}
                }
            }
        }
        json_data = self.do_api_request('v1/databases', body)
        return json_data["id"]

class BurpExtender(IBurpExtender, IHttpListener, ITab):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self.nw = None
        self.root_id = None
        self.notion_id_list = []
        self.notion_title_list = []
        self._helpers = callbacks.getHelpers()
        self.colName = [ 'Method', 'status', 'path' ]
        self.bigest_length = 0
        self.req_data = []
        self.drawUI()
        callbacks.registerHttpListener(self)
        callbacks.addSuiteTab(self)
        callbacks.setExtensionName("SiteMap To Notion")


    def drawUI(self):
        self.tab = swing.JPanel()
        # This part is just for the export button
        self.uiTitleLabel= swing.JLabel('Please set notion token and select the correct shared page before running:')
        self.uiTitleLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiTokenField = swing.JTextField('insert Token')
        self.uiTokenField.setPreferredSize(Dimension(200, 75))
        self.uiSaveToken = swing.JButton('Save Token',actionPerformed=self.wraperToExportNotion)
        # pick root page
        self.uiRootPageLabel = swing.JLabel('Select Page:')
        self.uiRootPageLabel.setFont(Font('Tahoma', Font.BOLD, 14))
        self.uiRootPagePane = swing.JScrollPane()
        # button to run export
        self.uiExportRun = swing.JButton('Export to Notion',actionPerformed=self.exportAndSaveToNotion)
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
                                                        .addComponent(self.uiTitleLabel)
                                                        .addComponent(self.uiTokenField)
                                                        .addComponent(self.uiSaveToken)
                                                        .addGap(15,15,15)
                                                        .addComponent(self.uiRootPageLabel)
                                                        .addComponent(self.uiRootPagePane)
                                                        .addGap(15,15,15)
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
                                            .addComponent(self.uiTitleLabel)
                                            .addGap(15,15,15)
                                            .addComponent(self.uiTokenField)
                                            .addGap(5,5,5)
                                            .addComponent(self.uiSaveToken)
                                            .addGap(15,15,15)
                                            .addComponent(self.uiRootPageLabel)
                                            .addGap(5,5,5)
                                            .addComponent(self.uiRootPagePane)
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

    def menu_click(self, event):
        print(self.uiRootList.selectedIndex)
        self.root_id = self.notion_id_list[self.uiRootList.selectedIndex]

    def wraperToExportNotion(self, e):
        tmp_token = self.uiTokenField.getText()
        self.nw = NotionWrapper(token=tmp_token)
        jdata = self.nw.get_pages()
        for data in jdata:
            print(data["parent"]["type"])
            if data["parent"]["type"] == "page_id":
                self.notion_id_list.append(data["id"])
                self.notion_title_list.append(data["properties"]["title"]["title"][0]["text"]["content"])
            else:
                print('parent is database skiping since no title available')
        self.uiRootList = swing.JList(self.notion_title_list, valueChanged=self.menu_click)
        self.uiRootPagePane.setViewportView(self.uiRootList)

    def exportAndSaveToNotion(self, e):
        # [ 'method', 'status', 'path_root', 'rest of path', ... ]
        root_saved = []
        api_id_root = []
        if self.nw == None or self.root_id == None:
            return

        db_id = self.nw.create_root_database_from_template(self.root_id)
        for line in self.req_data:
            if line[1] != '200': # ignore not 200 requests
                continue
            if line[2] in root_saved:
                self.nw.create_child_page_from_template(api_id_root[root_saved.index(line[2])], '/'.join(line[2:]), line[0])
            else:
                page_id = self.nw.create_root_page_from_template(db_id, line[2])
                inline_id = self.nw.create_inline_database_from_template(page_id)
                root_saved.append(line[2])
                api_id_root.append(inline_id)
                self.nw.create_child_page_from_template(inline_id, '/'.join(line[2:]), line[0])

    def populate_array(self, status, uri, method):
        data_uri = uri.split('/')[1:]
        if isinstance(data_uri, str) or len(data_uri) == 0:
            return
        data_uri = [sub if len(sub) else sub.replace('', '/') for sub in data_uri]
        data_uri.insert(0, status)
        data_uri.insert(0, method)
        if len(self.req_data) == 0:
            self.req_data.append(data_uri)
        else:
            i = 0
            j = 0
            while i < len(self.req_data) and j < len(data_uri):
                if self.bigest_length < len(data_uri):
                    self.bigest_length = len(data_uri)
                if data_uri in self.req_data:
                    return
                if j == len(self.req_data[i]):
                    i = i + 1
                    j = 0
                    continue
                if self.req_data[i][j] != data_uri[j]:
                    #split array and insert
                    self.req_data.insert(i, data_uri)
                    break
                else:
                    # elements are equal so go back up
                    j = j + 1
                    continue
        if self.bigest_length > len(self.colName):
            for i in range(len(self.colName), self.bigest_length):
                self.colName.append('path')
        dataModel = DefaultTableModel(self.req_data, self.colName)
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
