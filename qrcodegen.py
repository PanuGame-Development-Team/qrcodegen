from PyQt5.QtWidgets import QApplication,QWidget,QFileDialog,QMessageBox,QTableWidgetItem
from PyQt5.QtCore import pyqtSlot
from ui import Ui_Form
from io import StringIO
from datetime import datetime,timedelta
from random import randint
MAP = {i:str(i) for i in range(1,10)}
MAP.update({i:chr(i+55) for i in range(10,36)})
YMAP = {2025:"Y",2026:"L"}
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.btn_next.setDefault(True)
        self.newrow("0000","2.50","4200")
        self.ui.historyTable.resizeColumnsToContents()
    def newrow(self,id,vol,res):
        self.ui.historyTable.blockSignals(True)
        self.ui.historyTable.insertRow(0)
        self.ui.historyTable.setItem(0,0,QTableWidgetItem(str(id)))
        self.ui.historyTable.setItem(0,1,QTableWidgetItem(str(vol)))
        self.ui.historyTable.setItem(0,2,QTableWidgetItem(str(res)))
        self.ui.historyTable.setItem(0,3,QTableWidgetItem(self.generate(index=id,vol=vol,res=res)))
        self.ui.historyTable.blockSignals(False)
    @pyqtSlot(str)
    def on_index_textChanged(self):
        self.ui.output.setText(self.generate(htmlemphasize=True))
    @pyqtSlot()
    def on_index_returnPressed(self):
        self.ui.volume.setFocus()
    @pyqtSlot(str)
    def on_volume_textChanged(self):
        vol = self.ui.volume.text()
        while(vol and type(vol) != float):
            try:
                vol = float(vol)
            except:
                self.ui.volume.setText(vol[:-1])
                vol = self.ui.volume.text()
        self.ui.output.setText(self.generate(htmlemphasize=True))
    @pyqtSlot()
    def on_volume_returnPressed(self):
        self.ui.resistance.setFocus()
    @pyqtSlot(str)
    def on_resistance_textChanged(self):
        res = self.ui.resistance.text()
        while(res and type(res) != int):
            try:
                res = int(res)
            except:
                self.ui.resistance.setText(res[:-1])
                res = self.ui.resistance.text()
        self.ui.output.setText(self.generate(htmlemphasize=True))
    @pyqtSlot()
    def on_resistance_returnPressed(self):
        self.ui.btn_next.setFocus()
    @pyqtSlot()
    def on_btn_next_clicked(self):
        ind = self.ui.index.text()
        vol = self.ui.volume.text()
        res = self.ui.resistance.text()
        if not ind or not vol or not res:
            QMessageBox.warning(self,"警告","请输入 阻值 和 流量。")
            return
        try:
            vol = float(vol)
            res = int(res)
        except:
            QMessageBox.warning(self,"警告","阻值 或 流量 格式不是数字。")
            return
        if vol < 2.0 or vol > 3.0:
            QMessageBox.warning(self,"警告","流量范围错误。")
            return
        if res < 3780 or res > 4620:
            QMessageBox.warning(self,"警告","阻值范围错误。")
            return
        self.ui.index.setText("")
        self.ui.volume.setText("")
        self.ui.resistance.setText("")
        self.ui.output.setText("")
        self.ui.index.setFocus()
        self.newrow(ind,"%.2f"%vol,res)
    @pyqtSlot()
    def on_btn_export_clicked(self):
        now = datetime.now()
        filename = QFileDialog.getSaveFileName(self,"导出二维码信息",f"""qrcodegen-{now.strftime("%Y%m%d%H%M%S")}.txt""")[0]
        if not filename:
            return
        filename2 = QFileDialog.getSaveFileName(self,"导出二维码分割信息",f"""qrcodegen-{now.strftime("%Y%m%d%H%M")}.txt""")[0]
        if not filename2:
            return
        with open(filename,"w") as f:
            for i in range(self.ui.historyTable.rowCount()-1,-1,-1):
                f.write(self.ui.historyTable.item(i,3).text() + "\n")
        with open(filename2,"w") as f:
            for i in range(self.ui.historyTable.rowCount()-1,-1,-1):
                f.write(self.ui.historyTable.item(i,3).text()[12:23] + "\n")
    def on_historyTable_itemChanged(self,item):
        row = item.row()
        col = [self.ui.historyTable.item(row,i).text() for i in range(3)]
        self.ui.historyTable.blockSignals(True)
        self.ui.historyTable.setItem(row,3,QTableWidgetItem(self.generate(index=col[0],vol=col[1],res=col[2])))
        self.ui.historyTable.resizeColumnsToContents()
        self.ui.historyTable.blockSignals(False)
    def generate(self,index=None,vol=None,res=None,htmlemphasize=False):
        index = self.ui.index.text() if not index else index
        vol = self.ui.volume.text() if not vol else vol
        vol = "%.2f"%float(vol) if vol else ""
        res = self.ui.resistance.text() if not res else res
        now = datetime.now()
        fortune = now + timedelta(seconds=randint(80,100))
        fore = ""
        back = ""
        if htmlemphasize:
            fore = "<b><i>"
            back = "</i></b>"
        s = f"""02DD6200102AEANR{fore}{YMAP[now.year]}{MAP[now.month]}{MAP[now.day]}{index}{back}QRCNQ01T0012/{fore}{now.strftime("%Y%m%d%H%M%S")}{back}/{fore}{fortune.strftime("%Y%m%d%H%M%S")}{back}/A9033/{fore}{vol}{back}/3.00/2.00/A0321/{fore}{res}{back}/4620/3780/"""
        return s
app = QApplication(["qrcodegen"])
window = Window()
window.show()
app.exec_()