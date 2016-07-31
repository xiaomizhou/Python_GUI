import matplotlib
matplotlib.use('TKAgg')
from PyQt4.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
Ui_MainWindow, QMainWindow = loadUiType('MainWindow.ui')
import time
from datetime import datetime
import matplotlib.animation as animation
import numpy as np
from PyQt4 import QtCore, QtGui
import visa
import sys, csv
from time import sleep

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.axes.grid()
        self.axes.set_ylim(0,100)
        self.axes.set_xlim(0,50)
        self.axes.set_autoscalex_on(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass

class Main(QMainWindow, Ui_MainWindow):
	def __init__(self, ):
		super(Main, self).__init__()
		self.setupUi(self)
		QtCore.QObject.connect(self.scanButton,QtCore.SIGNAL('clicked()'), self.dispInstru)
		QtCore.QObject.connect(self.connectButton,QtCore.SIGNAL('clicked()'), self.connectInstru)
		QtCore.QObject.connect(self.configButton, QtCore.SIGNAL('clicked()'), self.loadConfigFile)
		QtCore.QObject.connect(self.saveButton, QtCore.SIGNAL('clicked()'), self.handleSave)
		QtCore.QObject.connect(self.modeComboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.changeMode)
		QtCore.QObject.connect(self.sweepButton, QtCore.SIGNAL('clicked()'), self.startSweep)

		self.canvas = MyMplCanvas(self, width=5, height=4, dpi=100)
		self.p = 0
		self.mplvl.addWidget(self.canvas)   #self.canvas.setParent(self.mplwindow)
		self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
		self.mplvl.addWidget(self.toolbar)

	def dispInstru(self):
		self.rm = visa.ResourceManager()
		self.instrusList = self.rm.list_resources()
		print self.instrusList
		for i in range(len(self.instrusList)):
			exec("self.instruCheckBox%s = QtGui.QCheckBox(self.verticalLayoutWidget)" % i)
			exec("self.instruCheckBox%s.setText(self.instrusList[%s])" % (i,i))
			exec("self.instruLayout.addWidget(self.instruCheckBox%s)" % i)
	def loadConfigFile(self):
		self.listWidget.addItem('Assign success')
		f = open('configure','r')
		lines = f.readlines()
		self.configMap = {}
		for line in lines:
			line = line.strip()
			IDN, instruName= line.split(' ')
			self.configMap[IDN] = instruName		
	def connectInstru(self):
		self.listWidget.addItem('Connect success')
		self.instruMap = {}
		self.instruObj = []
		for i in range(len(self.instrusList)):
			exec("a = self.instruCheckBox%s.isChecked()" % i)
			if a:
				instruName = self.configMap[self.instrusList[i]]
				self.instruMap[i] = instruName
				self.instruObj.append(self.rm.open_resource(self.instrusList[i]))
		for i in range(len(self.instruObj)):
			if self.instruMap[i] == '2400':
				self.instruObj[i].write("*RST")
				self.instruObj[i].write("*CLS")
				self.instruObj[i].write("*RCL 0")
			if self.instruMap[i] == '2636' or self.instruMap[i] == '2635A':
				self.instruObj[i].write("reset()")
				self.instruObj[i].write("*CLS")
	def handleSave(self):
		path = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
		if not path.isEmpty():
			with open(unicode(path), 'wb') as stream:
				writer = csv.writer(stream)
				for row in range(self.tableWidget.rowCount()):
					rowdata = []
					for column in range(self.tableWidget.columnCount()):
						item = self.tableWidget.item(row, column)
						if item is not None:
							rowdata.append(unicode(item.text()).encode('utf8'))
						else:
							rowdata.append('')
					print rowdata
					writer.writerow(rowdata)
	def changeMode(self):
		if self.modeComboBox.currentText() == 'Voltage Sweep':
			self.startLabel = QtGui.QLabel('')
			self.startLabel.setText('Start')
			self.startLabel.setStyleSheet("font: 18pt \"Helvetica\";\n""border-color: rgb(0, 0, 0);")
			self.startLineEdit = QtGui.QLineEdit()
			self.paraLayout.addRow(self.startLabel,self.startLineEdit)

			self.stepLabel = QtGui.QLabel('')
			self.stepLabel.setText('Step')
			self.stepLabel.setStyleSheet("font: 18pt \"Helvetica\";\n""border-color: rgb(0, 0, 0);")
			self.stepLineEdit = QtGui.QLineEdit()
			self.paraLayout.addRow(self.stepLabel,self.stepLineEdit)

			self.stopLabel = QtGui.QLabel('')
			self.stopLabel.setText('Stop')
			self.stopLabel.setStyleSheet("font: 18pt \"Helvetica\";\n""border-color: rgb(0, 0, 0);")
			self.stopLineEdit = QtGui.QLineEdit()
			self.paraLayout.addRow(self.stopLabel,self.stopLineEdit)

			self.complianceLabel = QtGui.QLabel('')
			self.complianceLabel.setText('Compliance')
			self.complianceLabel.setStyleSheet("font: 18pt \"Helvetica\";\n""border-color: rgb(0, 0, 0);")
			self.complianceLineEdit = QtGui.QLineEdit()
			self.paraLayout.addRow(self.complianceLabel,self.complianceLineEdit)

			self.delayLabel = QtGui.QLabel('')
			self.delayLabel.setText('Delay')
			self.delayLabel.setStyleSheet("font: 18pt \"Helvetica\";\n""border-color: rgb(0, 0, 0);")
			self.delayLineEdit = QtGui.QLineEdit()
			self.paraLayout.addRow(self.delayLabel,self.delayLineEdit)
	def startSweep(self):
		self.onStart()

		# if self.modeComboBox.currentText == 'Voltage Sweep':
		# 	compliance = int(self.complianceLineEdit.getText())
		# 	start = int(self.startLineEdit.getText())
		# 	stop = int(self.stopLineEdit.getText())
		# 	step = int(self.stepLineEdit.getText())
		# 	pointsNum = (stop-start)/step + 1
		# 	i = self.instruMap.keys()[self.instruMap.values().index('2400')]
		# 	self.instruObj[i].write("*RST")  #restore GPIB default conditions
		# 	self.instruObj[i].write(":SOUR:FUNC VOLT") #source is voltage
		# 	self.instruObj[i].write(":SENS:FUNC 'CURR:DC") #sense is Current
		# 	self.instruObj[i].write(":SENS:CURR:PROT %d" % compliance) #voltage protection
		# 	self.instruObj[i].write(":SOUR:VOLT:START %f" % start)
		# 	self.instruObj[i].write(":SOUR:VOLT:STOP %f" % stop)
		# 	self.instruObj[i].write(":SOUR:VOLT:STEP %f" % step)
		# 	self.instruObj[i].write(":SOUR:VOLT:MODE SWE") # sweep mode
		# 	self.instruObj[i].write(":SOUR:SWE:RANGE AUTO") #auto source ranging
		# 	self.instruObj[i].write(":SOUR:SWE:SPAC LIN") #select linear staricase sweep
		# 	self.instruObj[i].write(":TRIG:COUNT %d" % pointsNum)
		# 	self.instruObj[i].write(":SOUR:DEL 0.1")
		# 	self.instruObj[i].write(":FORM:ELEM CURR")  #current reading only
		# 	self.instruObj[i].write(":OUTP ON")
		# 	self.instruObj[i].write(":READ?")
		# 	aa = self.instruObj[i].read()

	def onStart(self):
		self.x = []
		self.y = []
		self.canvas.axes.set_autoscalex_on(True)
		self.line, = self.canvas.axes.plot(self.x,self.y)
		timer = QtCore.QTimer(self)
		timer.timeout.connect(self.run)
		timer.start(10)
		#self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)
		#self.ani = animation.FuncAnimation(self.canvas.figure,self.run,self.data_gen, blit=True, interval = 100)
	# def data_gen(self):
	# 	while True:
	# 		self.p = -1*self.p
	# 		t = max(self.x) + 1
	# 		y = np.sin(t)
	# 		yield t,y
	def run(self):
		newx = max(self.x) + 1
		self.x.append(newx)
		self.y = np.sin(self.x)
		self.line.set_data(self.x, self.y)
		xmin,xmax = self.canvas.axes.get_xlim()
		ymin,ymax = self.canvas.axes.get_ylim()
		self.canvas.axes.figure.canvas.draw()
		if newx >= xmax:
			xmax = 2*xmax
			self.canvas.axes.set_xlim(0,xmax)
			self.canvas.axes.figure.canvas.draw()
			QtGui.qApp.processEvents()     #update the window to see the new x scale !important canvas.draw() must go before this line				
		self.tableWidget.insertRow(self.p)
		self.tableWidget.setItem(self.p,0,QtGui.QTableWidgetItem(datetime.now().strftime("%H:%M:%S.%f")))
		self.tableWidget.setItem(self.p,1,QtGui.QTableWidgetItem(str(newx)))
		self.tableWidget.setItem(self.p,2,QtGui.QTableWidgetItem(str(self.y[-1])))
		self.p += 1


		# newx, newy = data
		# self.x.append(newx)
		# self.y = np.sin(self.x)
		# self.line.set_data(self.x, self.y)
		# xmin,xmax = self.canvas.axes.get_xlim()
		# ymin,ymax = self.canvas.axes.get_ylim()
		# if newx >= xmax:
		# 	xmax = 2*xmax
		# 	self.canvas.axes.set_xlim(0,xmax)
		# 	self.canvas.axes.figure.canvas.draw()
		# 	QtGui.qApp.processEvents()     #update the window to see the new x scale !important canvas.draw() must go before this line		
		# return self.line,
		# self.fig_dict = {}
		# self.mplfigs.itemClicked.connect(self.addNumber)

	# def addNumber(self, item):
	# 	text = str(item.text())
	# 	self.rmmpl()
	# 	self.addmpl(self.fig_dict[text])

	# def addfig(self, name, fig):
	# 	self.fig_dict[name]  = fig
	# 	self.mplfigs.addItem(name)
	def init(self):
		self.x.append(1)
		self.x.append(2)
		self.y.append(4)
		self.y.append(-5)
		self.line.set_data(self.x, self.y)
		

	def rmmpl(self, ):
		self.mplvl.removeWidget(self.canvas)
		self.canvas.close()
		self.mplvl.removeWidget(self.toolbar)
		self.toolbar.close()


if __name__=='__main__':
	import sys
	from PyQt4 import QtGui
	import numpy as np
	app = QtGui.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())