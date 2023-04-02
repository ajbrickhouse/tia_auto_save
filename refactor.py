import sys
import clr
import schedule
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QSpinBox, QProgressBar, QWidget
from PyQt5.QtCore import QTimer

clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V16\\PublicAPI\\V16\\Siemens.Engineering.dll')

import Siemens.Engineering as tia

class TiaConnect(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tia Auto Save")
        self.setGeometry(300, 300, 280, 165)
        self.setFixedSize(280, 165)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        self.cb_avail_jobs = QComboBox()
        top_layout.addWidget(self.cb_avail_jobs)

        self.btn_refresh = QPushButton("Refresh")
        top_layout.addWidget(self.btn_refresh)

        interval_layout = QHBoxLayout()
        main_layout.addLayout(interval_layout)

        self.spn_interval = QSpinBox()
        self.spn_interval.setRange(1, 100)
        interval_layout.addWidget(self.spn_interval)

        self.btn_start_saving = QPushButton("Start Saving")
        interval_layout.addWidget(self.btn_start_saving)

        self.pb_time_left = QProgressBar()
        self.pb_time_left.setMaximum(0)
        main_layout.addWidget(self.pb_time_left)

        self.lbl_time_left = QLabel("Time Left: -- min and -- sec")
        main_layout.addWidget(self.lbl_time_left)

        self.sched_enabled = False
        self.refresh()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.parallel_loop)
        self.timer.start(250)

        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_start_saving.clicked.connect(self.btn_start_toggle)
        self.spn_interval.valueChanged.connect(self.set_save_interval)
        self.cb_avail_jobs.currentIndexChanged.connect(self.set_job_selection)

    def parallel_loop(self):
        if self.sched_enabled:
            schedule.run_pending()

            value = self.pb_time_left.value()
            self.pb_time_left.setValue(value + 1)

            percent_comp = int(round((value / self.interval_sec) * 100, 0))
            self.setWindowTitle(f"Tia Auto Save - {percent_comp}%")

            time_left = round((self.interval_sec - value) / 60, 2)
            min_left = int(time_left)
            sec_left = int(round((time_left - min_left) * 60, 0))

            self.lbl_time_left.setText(f"Next Save in {min_left} minutes and {sec_left} seconds.")
            self.btn_start_saving.setText("Stop Saving")
            self.btn_start_saving.setStyleSheet("background-color: red")
        else:
            self.pb_time_left.setValue(0)
            self.setWindowTitle("Tia Auto Save")
            self.lbl_time_left.setText("Next Save in -- min and -- sec.")
            self.btn_start_saving.setText("Start Saving")
            self.btn_start_saving.setStyleSheet("background-color: green")

    def save_project(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S.%f")
        self.pb_time_left.setValue(0)

        try:
            self.myproject.Save()
            print(current_time, "File Saved...")
        except Exception as e:
            print(current_time,
                  "Save Failed...\n",
                  "--------------------------------------------------------\n",
                  e,
                  "\n--------------------------------------------------------\n")

    def refresh(self):
        self.get_processes()
        self.get_job_info()

    def get_processes(self):
        self.processes = tia.TiaPortal.GetProcesses()
        self.process_found = len(self.processes) > 0

    def get_job_info(self):
        self.jobs = []
        self.paths = []

        if self.process_found:
            for process in self.processes:
                process_path = str(process.ProjectPath)
                self.paths.append(process_path.replace("\\", "\\\\"))
                paths_split = process_path.split("\\")
                self.jobs.append(paths_split[-1])

            self.cb_avail_jobs.clear()
            self.cb_avail_jobs.addItems(self.jobs)
        else:
            self.cb_avail_jobs.clear()
            self.cb_avail_jobs.addItem('No Processes Found')

    def btn_start_toggle(self):
        self.sched_enabled = not self.sched_enabled

    def set_job_selection(self, index):
        if self.process_found:
            self.selected_job = self.jobs[index]
            self.selected_job_index = index

            print("\nSelected Job: ", self.selected_job)
            print("Selected Job Loc: ", self.paths[self.selected_job_index])

            self.sched_enabled = False

            self.mytia = self.processes[self.selected_job_index].Attach()
            self.myproject = self.mytia.Projects[0]

    def set_save_interval(self, interval):
        self.interval_sec = interval * 60
        self.pb_time_left.setMaximum(self.interval_sec)
        self.pb_time_left.setValue(0)

        schedule.clear()
        schedule.every(interval).minutes.do(self.save_project)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TiaConnect()
    main_window.show()
    sys.exit(app.exec_())

