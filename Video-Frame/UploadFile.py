import sys
from PyQt5.QtWidgets import QWidget, QFileDialog

class FileDialog(QWidget):

	def __init__(self):
		super().__init__()
		self.openFileDialog()
		
	def openFileDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", "/home", "Images (*.png *.xpm *.jpg)", options=options)
		if fileName:
			print(fileName)



