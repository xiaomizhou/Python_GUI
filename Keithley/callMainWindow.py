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
import numpy

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        self.axes.grid()
        self.axes.set_ylim(0,1)
        self.axes.set_xlim(-1,1)
        self.axes.set_autoscalex_on(True)
        self.compute_initial_figure()
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
		QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL('clicked()'), self.stopSweep)
		QtCore.QObject.connect(self.pauseButton, QtCore.SIGNAL('clicked()'), self.pauseSweep)


		self.canvas = MyMplCanvas(self, width=5, height=4, dpi=100)
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
		self.instruMap = []
		self.instruObj = []
		for i in range(len(self.instrusList)):
			exec("a = self.instruCheckBox%s.isChecked()" % i)
			if a:
				instruName = self.configMap[self.instrusList[i]]
				self.instruMap.append(instruName)
				self.instruObj.append(self.rm.open_resource(self.instrusList[i]))
		for i in range(len(self.instruObj)):
			print 'I am here 1'
			print self.instruMap[i]
			if self.instruMap[i] == '2400':
				self.instruObj[i].write("*RST")
				self.instruObj[i].write("*CLS")
				self.instruObj[i].write("*RCL 0")
				print 'I am here 2'
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
			print 'I am changeMode'
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
		print 'I am startSweep 1'
		currentRow = self.listWidget.count()
		lastContent = self.listWidget.item(currentRow-1).text()
		if lastContent!='Sweep stop' and currentRow>2:
			self.p = 0
			self.listWidget.addItem('Please stop the sweep first!')
		else:
			self.listWidget.addItem('Sweep start')
			print 'I am startSweep 2'
			self.onStart()
	def stopSweep(self):
		self.listWidget.addItem('Sweep stop')
		self.timer.stop()
	def pauseSweep(self):
		pass
		

	def onStart(self):
		print 'I am onStart first'
		self.p = 0
		if self.modeComboBox.currentText() == 'Voltage Sweep':  # for 2400 instrument
			print 'I am onStart'
			compliance = float(self.complianceLineEdit.text())
			start = float(self.startLineEdit.text())
			stop = float(self.stopLineEdit.text())
			sourceR = stop + 1
			step = float(self.stepLineEdit.text())
			self.sourceList = numpy.arange(start,stop+step,step)
			self.curInstruNo = self.instruMap.index('2400')	# get current instrument index in intruMap		
			self.instruObj[self.curInstruNo].write("*RST")  #restore GPIB default conditions
			self.instruObj[self.curInstruNo].write(":ROUT:TERM FRONT") 
			self.instruObj[self.curInstruNo].write(":SOUR:FUNC VOLT") #source is voltage
			self.instruObj[self.curInstruNo].write(":SOUR:VOLT:MODE FIXED") # sweep mode
			self.instruObj[self.curInstruNo].write(":SOUR:VOLT:RANGE %f" % sourceR) #auto source ranging
			self.instruObj[self.curInstruNo].write(":SENS:FUNC 'CURR:DC'") #sense is Current
			self.instruObj[self.curInstruNo].write(":SENS:CURR:PROT %f" % compliance) #voltage protection
			self.instruObj[self.curInstruNo].write(":SENS:CURR:RANG 1e-2")
			self.instruObj[self.curInstruNo].write(":FORM:ELEM CURR")  #current reading only
			print 'I am onStart 2'
			self.x = []
			self.y = []
			self.canvas.axes.set_autoscalex_on(True)
			self.line, = self.canvas.axes.plot(self.x,self.y)
			self.instruObj[self.curInstruNo].write(":OUTP ON")
			for isource in self.sourceList:
				self.instruObj[self.curInstruNo].write(":SOUR:VOLT:LEV %f" % isource) #auto source ranging	
				
				time.sleep(2)
				self.instruObj[self.curInstruNo].write(":READ?")
				time.sleep(1)
				senseRead = float(self.instruObj[self.curInstruNo].read())
				
				newx = isource
				newy = senseRead 
				self.x.append(newx)
				self.y.append(newy)
				self.line.set_data(self.x, self.y)
				xmin,xmax = self.canvas.axes.get_xlim()
				ymin,ymax = self.canvas.axes.get_ylim()
				self.canvas.axes.figure.canvas.draw()
				if max(self.x) >= xmax:
					xmax = 2*xmax
					self.canvas.axes.set_xlim(xmin,xmax)
					self.canvas.axes.figure.canvas.draw()
					QtGui.qApp.processEvents()     #update the window to see the new x scale !important canvas.draw() must go before this line				
				self.tableWidget.insertRow(self.p)
				self.tableWidget.setItem(self.p,0,QtGui.QTableWidgetItem(datetime.now().strftime("%H:%M:%S.%f")))
				self.tableWidget.setItem(self.p,1,QtGui.QTableWidgetItem(str(newx)))
				self.tableWidget.setItem(self.p,2,QtGui.QTableWidgetItem(str(self.y[-1])))
				self.p += 1
			self.instruObj[self.curInstruNo].write(":OUTP OFF")

	# 		self.timer = QtCore.QTimer(self)
	# 		self.iSource = 0
	# 		self.timer.timeout.connect(self.run)
	# 		self.timer.start(2000)
	# def run(self):
	# 	print 'I am run'
	# 	self.instruObj[self.curInstruNo].write(":SOUR:VOLT:LEV %f" % self.sourceList[self.iSource]) #auto source ranging
	# 	time.sleep(2)		
	# 	self.instruObj[self.curInstruNo].write(":OUTP ON")
	# 	time.sleep(2)
	# 	self.instruObj[self.curInstruNo].write(":READ?")
	# 	time.sleep(1)
	# 	senseRead = float(self.instruObj[self.curInstruNo].read())
	# 	self.instruObj[self.curInstruNo].write(":OUTP OFF")
	# 	.append(self.sourceList[self.iSource])
	# 	newx = self.sourceList[self.iSource]
	# 	newy = senseRead 
	# 	self.x.append(newx)
	# 	self.y.append(newy)
	# 	self.line.set_data(self.x, self.y)
	# 	xmin,xmax = self.canvas.axes.get_xlim()
	# 	ymin,ymax = self.canvas.axes.get_ylim()
	# 	self.canvas.axes.figure.canvas.draw()
	# 	if max(self.x) >= xmax:
	# 		xmax = 2*xmax
	# 		self.canvas.axes.set_xlim(0,xmax)
	# 		self.canvas.axes.figure.canvas.draw()
	# 		QtGui.qApp.processEvents()     #update the window to see the new x scale !important canvas.draw() must go before this line				
	# 	self.tableWidget.insertRow(self.p)
	# 	self.tableWidget.setItem(self.p,0,QtGui.QTableWidgetItem(datetime.now().strftime("%H:%M:%S.%f")))
	# 	self.tableWidget.setItem(self.p,1,QtGui.QTableWidgetItem(str(newx)))
	# 	self.tableWidget.setItem(self.p,2,QtGui.QTableWidgetItem(str(self.y[-1])))
	# 	self.p += 1
	# 	self.iSource += 1

	# 	if self.iSource == len(self.sourceList):
	# 		self.timer.stop()
	# 		self.listWidget.addItem('Sweep stop')



if __name__=='__main__':
	import sys
	from PyQt4 import QtGui
	import numpy as np
	app = QtGui.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())