import sys
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout
from PyQt5.uic import loadUi
from matplotlib import image

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import gs_beam_retrieval as retrieval
import visualizations

class MainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.app = app
        self.ui = loadUi('../mainwindow.ui', self)

        #Connect buttons
        buttons = ["choose_image_before_focus_button", "choose_image_behind_focus_button", "run_button"]
        for button_name in buttons:
            component = getattr(self.ui, button_name)
            component.clicked.connect(getattr(self, f'on_{button_name}'))

        #Add plot widgets to ui, and collect all axis in self.pyplot_axs
        original_images_fig = self.insert_figure("original_images_box")
        original_images_fig.subplots(1, 2)

        reconstructed_field_fig = self.insert_figure("reconstructed_field_box")
        self.plot_handles = {
            "original_images": original_images_fig,
            "reconstructed_field": reconstructed_field_fig,
        }

        self.ui.show()
        self.ui.raise_()
    
    #Button and other actions

    def on_choose_image_before_focus_button(self):
        self.ui.image_before_focus_path.setText(self.open_image("Image Before Focus"))
        self.on_image_before_focus_path()
    
    def on_image_before_focus_path(self):
        before = image.imread(self.ui.image_before_focus_path.text())
        self.set_fig_image(before, "original_images", 0)

    def on_choose_image_behind_focus_button(self):
        self.ui.image_behind_focus_path.setText(self.open_image("Image Behind Focus"))
        self.on_image_behind_focus_path()
    
    def on_image_behind_focus_path(self):
        behind = image.imread(self.ui.image_behind_focus_path.text())
        self.set_fig_image(behind, "original_images", 1)
    
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

    def on_beam_retrieved(self, F):
        visualizations.interactive_field(self.plot_handles["reconstructed_field"], F, float(self.ui.distance_to_focus.text()))


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
    
    def set_fig_image(self, image, plot_handle, axis):
        h, w = image.shape
        self.plot_handles[plot_handle].axes[axis].imshow(image, extent=[0, w, h,0])
        self.plot_handles[plot_handle].set_tight_layout(True)
        self.plot_handles[plot_handle].canvas.draw()
    
class BeamRetrievalThread(QThread):

    def __init__(self, parent, data, callback):
        QThread.__init__(self, parent)
        self.data = data
        self.callback = callback

    def __del__(self):
        self.wait()


    def run(self):
        F = retrieval.gs_beam_retrieval(**self.data)
        self.callback(F)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())