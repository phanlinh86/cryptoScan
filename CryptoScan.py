from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
import sys
import urllib.request
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as po

BSC_API_KEYS    = "9WAACQY2JYQDVU7V1B7NZH9WSQ154DQBJI"
BSC_UNIT        = 1e18 # Data return from BSC is 1/e18 BNB

class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class cryptoScan(QtWidgets.QMainWindow):
    """
    @class cryptoAlarm
    @brief This class hold all functions/attributes related to cryptoALarm application
    """
    def __init__(self):
        """
        @fn __init__
        @brief This constructor  to initialize attributes for class cryptoAlarm
        @param None
        """
        super(cryptoScan, self).__init__()
        self.setupUi()
        self.connectUi()
        #self.initializeUi()
        #self.initializeDatabase()
        #self.setupTimer()

    def setupUi(self):
        self.setUpCentralWidget()
        self.setUpTextAddress()
        self.setUpLabelAddress()
        self.setUpMenuBar()
        self.setUpLabelStatus()
        self.setUpTableDisplay()
        self.setUpfigView()

        #self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(self.centralwidget)

    def setUpCentralWidget(self):
        """
        @fn setUpCentralWidget
        @brief  This function to set up UI central widget
        @param  None
        @return None
        """
        self.setObjectName("MainWindow")
        self.resize(700, 800)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("Crypto Scan")

    def setUpLabelAddress(self):
        self.labelAddress = QtWidgets.QLabel(self.centralwidget)
        self.labelAddress.setGeometry(QtCore.QRect(70, 31, 51, 20))
        self.labelAddress.setObjectName("labelAddress")
        self.labelAddress.setText("Address")

    def setUpTextAddress(self):
        self.textAddress = QtWidgets.QTextEdit(self.centralwidget)
        self.textAddress.setGeometry(QtCore.QRect(70, 50, 511, 41))
        self.textAddress.setObjectName("textAddress")
        self.textAddress.setText("Seach by Address / Txn Hash / Block / Token ...")
        self.textAddress.setAcceptRichText(False)

    def setUpLabelStatus(self):
        self.labelStatus = QtWidgets.QLabel(self.centralwidget)
        self.labelStatus.setGeometry(QtCore.QRect(80, 310, 491, 21))
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setText("")

    def setUpMenuBar(self):
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 686, 21))
        self.menubar.setObjectName("menubar")
        self.menuAction = QtWidgets.QMenu(self.menubar)
        self.menuAction.setObjectName("menuAction")
        self.setMenuBar(self.menubar)
        self.actionCheckRoute = QtWidgets.QAction(self.menubar)
        self.actionCheckRoute.setObjectName("actionCheckRoute")
        self.actionTopHolders = QtWidgets.QAction(self.menubar)
        self.actionTopHolders.setObjectName("actionTopHolders")
        self.menuAction.addAction(self.actionCheckRoute)
        self.menuAction.addAction(self.actionTopHolders)
        self.menubar.addAction(self.menuAction.menuAction())
        self.menuAction.setTitle("Edit")
        self.menuAction.setTitle("Action")
        self.actionCheckRoute.setText("Check Route")
        self.actionTopHolders.setText("Top Holders")
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def setUpTableDisplay(self):
        self.tableDisplay = QtWidgets.QTableView(self.centralwidget)
        self.tableDisplay.setGeometry(QtCore.QRect(70, 100, 500, 700))
        self.tableDisplay.setObjectName("tableDisplay")

    def setUpfigView(self):
        self.figView = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        self.figView.setGeometry(QtCore.QRect(70, 100, 500, 700))

    # For table pa


    # UI Event related functions ***************************************************************************************
    def connectUi(self):
        self.textAddress.installEventFilter(self)  # Add listener for ticker texbox

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:# and source is self.textAddress:
            if event.button() == QtCore.Qt.RightButton:
                self.textAddressMouseClickEvent()

        if event.type() == QtCore.QEvent.KeyPress and source is self.textAddress:
            if event.key() in [QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter] and self.textAddress.hasFocus():
                self.address = self.textAddress.toPlainText().strip()
                print("Address: %s" % self.address)
                self.doSearchTransactionByAddress()

        return super(cryptoScan,self).eventFilter(source, event)

    def textAddressMouseClickEvent(self):
        self.textAddress.setText("")

    def doSearchTransactionByAddress(self):
        try:
            dfResult = self.getBscTransactionData()
            dfSankeyValue, sankeyLabel = self.processRawBscDataToSankeyFormat(dfResult)
            self.showShankey(dfSankeyValue,sankeyLabel)
        except Exception as err:
            print(err)

    def getBscTransactionData(self):
        url =   "https://api.bscscan.com/api" \
                + "?module=account" \
                + "&action=txlist" \
                + "&address=" + self.address \
                + "&startblock=0" \
                + "&endblock=99999999" \
                + "&page=1" \
                + "&offset=10000" \
                + "&sort=asc" \
                + "&apikey=" + BSC_API_KEYS
        data    = urllib.request.urlopen(url).read()
        pd.set_option('display.expand_frame_repr', False)
        #print(data)
        res = json.loads(data)
        dfResult = pd.DataFrame(res['result'])
        #print(dfResult)
        return dfResult
        # model = DataFrameModel(dfResult)
        # self.tableDisplay.setModel(model)

    def processRawBscDataToSankeyFormat(self,dfResult):
        dfSankey = dfResult[['from', 'to', 'value']]
        dfSankey.loc[:,'value'] = dfSankey.loc[:,'value'].astype(float).copy() / BSC_UNIT # Need to put a copy to avoid chain assignment warning
        #print(dfSankey)

        pivotSankey = pd.pivot_table(dfSankey, values='value', index=['from', 'to'], aggfunc=sum)
        dfSankeyValue = pivotSankey.reset_index()
        sankeyLabel = pd.unique(dfSankeyValue[['from', 'to']].values.ravel()).tolist()
        sankeyIndex = range(0, len(sankeyLabel))
        dictSankeyMap = dict(zip(sankeyLabel, sankeyIndex))
        dfSankeyValue = dfSankeyValue.replace(dictSankeyMap)
        #print(dfSankeyValue)
        return (dfSankeyValue,sankeyLabel)

    def showShankey(self,dfSankeyValue,sankeyLabel):
        colorLabel = len(sankeyLabel) * ["grey"]
        indexAddress = sankeyLabel.index(self.address.lower()) # Raw data from BscScan returns address in lower case
        colorLabel[indexAddress] = "red"
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=10,
                line=dict(color="black", width=0.5),
                label=sankeyLabel,
                color=colorLabel
            ),
            link=dict(
                source=dfSankeyValue['from'].tolist(),  # indices correspond to labels, eg A1, A2, A1, B1, ...
                target=dfSankeyValue['to'].tolist(),
                value=dfSankeyValue['value'].tolist()
            ))])
        fig.update_layout(title_text="Token flow of wallet %s in BscScan" % self.address, font_size=12)
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'

        #fig_view.setObjectName("tableDisplay")
        # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
        # for large figures.
        self.figView.setHtml(raw_html)
        self.figView.show()
        self.figView.raise_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = cryptoScan()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
