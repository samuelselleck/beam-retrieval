import sys
import os 

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout
from PyQt5.uic import loadUi
from matplotlib import image

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import field_retrieval as retrieval
import visualizations

SCRIPT_DIR = os.path.realpath(sys.path[0])

class MainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.app = app
        self.ui = loadUi(f'{SCRIPT_DIR}/../mainwindow.ui', self)

        #Connect ui with functions
        buttons = ["choose_image_before_focus_button", "choose_image_behind_focus_button", "run_button"]
        for button_name in buttons:
            component = getattr(self.ui, button_name)
            component.clicked.connect(getattr(self, f'on_{button_name}'))

        self.ui.image_before_focus_path.returnPressed.connect(self.on_image_before_focus_path)
        self.ui.image_behind_focus_path.returnPressed.connect(self.on_image_behind_focus_path)

        #Add plot widgets to ui, and collect all figures in self.pyplot_axs

        self.plot_handles = {
            "original_images": self.insert_figure("original_images_box"),
            "reconstructed_field": self.insert_figure("interactive_box"),
            "focus_field": self.insert_figure("slices_box"),
            "profile": self.insert_figure("profile_box"),
            "farfield": self.insert_figure("farfield_box"),
        }

        self.image_before = None
        self.image_behind = None

        self.ui.show()
        self.ui.raise_()
    
    #Button and other actions

    def on_choose_image_before_focus_button(self):
        self.ui.image_before_focus_path.setText(self.open_image("Image Before Focus"))
        self.on_image_before_focus_path()
    
    def on_image_before_focus_path(self):
        self.image_before = image.imread(self.ui.image_before_focus_path.text())
        visualizations.set_fig_images(self.plot_handles["original_images"], self.image_before, self.image_behind)

    def on_choose_image_behind_focus_button(self):
        self.ui.image_behind_focus_path.setText(self.open_image("Image Behind Focus"))
        self.on_image_behind_focus_path()
    
    def on_image_behind_focus_path(self):
        try:
            self.image_behind = image.imread(self.ui.image_behind_focus_path.text())
            visualizations.set_fig_images(self.plot_handles["original_images"], self.image_before, self.image_behind)
        except:
            self.show_message("could not import behind focus file, does it exist?")
    
    def on_run_button(self):
        data = {
            "before_focus_intensity": image.imread(self.ui.image_before_focus_path.text()),
            "behind_focus_intensity": image.imread(self.ui.image_behind_focus_path.text()),
            "dist_to_focus": float(self.ui.distance_to_focus.text()),
            "pixel_size": float(self.ui.pixel_size.text()),
            "wavelength": float(self.ui.wavelength.text()),
            "iterations": self.ui.iterations.value(),
        }

        retrieval = BeamRetrievalThread(self, data, self.on_beam_retrieved)      
        retrieval.start()

    def on_beam_retrieved(self, F_behind):
        dist_to_focus = float(self.ui.distance_to_focus.text())
        pixel_size = float(self.ui.pixel_size.text())
        visualizations.interactive_field(self.plot_handles["reconstructed_field"], F_behind, dist_to_focus)
        visualizations.plot_fields(self.plot_handles["focus_field"], F_behind, dist_to_focus)
        visualizations.plot_profile(self.plot_handles["profile"], F_behind, dist_to_focus, pixel_size)
        visualizations.plot_farfield(self.plot_handles["farfield"], F_behind, dist_to_focus, pixel_size)

    #Helper functions

    def open_image(self, title):
        return QFileDialog.getOpenFileName(self.ui, title, "~/Desktop", "Image Files (*.png *.jpg *.bmp)")[0]
    
    def insert_figure(self, widget_name):
        figure_widget = FigureCanvas(Figure())
        toolbar = NavigationToolbar(figure_widget, self)
        box = getattr(self.ui, widget_name)
        box.addWidget(toolbar)
        box.addWidget(figure_widget)
        return figure_widget.figure
    
    def show_message(self, message):
        print("MESSAGE:", message)
    
class BeamRetrievalThread(QThread):

    def __init__(self, parent, data, callback):
        QThread.__init__(self, parent)
        self.data = data
        self.callback = callback

    def __del__(self):
        self.wait()


    def run(self):
        F = retrieval.mgsa_field_retrieval(**self.data)
        self.callback(F)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())