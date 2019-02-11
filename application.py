from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from lib.dojo_requests import SUPPORTED_BROWSERS
from lib.actions import save_grades
from setting import config, save_settings


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        """
        Uses the UI from PyQt5 designer
        :param args:
        :param kwargs:
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('gui.ui', self)

        # Save Path Text
        self.save_path_ln.setText(config['file_config']['name'])

        # Save Path Button
        self.save_path_btn.clicked.connect(self.file_saveas)

        # Browser Support Checkbox
        self.browser_cb.addItems(SUPPORTED_BROWSERS)
        self.browser_cb.setCurrentIndex(SUPPORTED_BROWSERS.index(config['browser']))
        self.browser_cb.currentIndexChanged.connect(self.browser_change)

        # Overwrite Button
        checked = True if config['file_config']['overwrite'] == 'true' else False
        self.overwrite_chbx.setChecked(checked)
        self.overwrite_chbx.stateChanged.connect(self.overwrite_box)

        # Download Grades
        self.download_grades_btn.clicked.connect(self.save_grades)

        self.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        try:
            with open(path, 'rU') as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            # Qt will automatically try and guess the format as txt/html
            self.editor.setText(text)
            self.update_title()

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        try:
            print(self.path)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                                              "CSV documents (*.csv)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        try:
            with open(path, 'w') as f:
                f.write('tmp')

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            config['file_config']['name'] = path
            self.save_path_ln.setText(path)
            return path

    def save_grades(self):
        file_name = config['file_config'].get('name', None)
        if not len(file_name) > 0:
            file_name = self.file_saveas()
            if not file_name:
                return
        search_term = self.search_ln.text()
        config['search_term'] = search_term
        try:
            self.status_ln.setText("Downloading Grades")
            save_grades(file_name, search_term)
            self.status_ln.setText("Done")
        except EnvironmentError:
            self.status_ln.setText("Error: Browser not logged in")

    def browser_change(self, i):
        config['browser'] = self.browser_cb.itemText(i)
        return self.browser_cb.itemText(i)

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self, "Message",
            "Would you like to save the current configuration before quitting?",
            QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
            QMessageBox.Save)

        if reply == QMessageBox.Close:
            event.accept()
        elif reply == QMessageBox.Save:
            save_settings()
            event.accept()
        else:
            event.ignore()

    def overwrite_box(self, state):
        if state == QtCore.Qt.Checked:
            config['file_config']['overwrite'] = 'true'
        else:
            config['file_config']['overwrite'] = 'false'
