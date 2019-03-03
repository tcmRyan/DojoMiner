import sys
from application import MainWindow
from PyQt5.QtWidgets import QApplication
from apscheduler.schedulers.qt import QtScheduler
from lib.actions import scheduled_work


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook
    window = MainWindow()

    scheduler = QtScheduler()
    scheduler.remove_all_jobs()
    scheduler.add_job(scheduled_work, 'interval', minutes=60)
    scheduler.start()
    sys.exit(app.exec_())
