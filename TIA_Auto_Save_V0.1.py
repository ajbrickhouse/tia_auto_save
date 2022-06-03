from tkinter import messagebox
import clr
import schedule
import tkinter as tk
from datetime import datetime
from tkinter import HORIZONTAL, LEFT, X, Y, ttk

# Change this to your installed location
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V16\\PublicAPI\\V16\\Siemens.Engineering.dll')

# Import from TIA Portal API DLL referenced above
import Siemens.Engineering as tia

class tia_connect(tk.Tk):
    def __init__(self):
        ''' Initial call, define window and elements'''
        super().__init__()

        self.title("Tia Auto Save")
        self.geometry("280x140")
        self.resizable(False, False)
        self.attributes('-topmost',True)  

        ''' FRAMES --------------------------------------------------------------------'''
        ''' Left side frame '''

        leftframe_ = tk.Frame(self)
        leftframe_.grid(row=0, column=0, rowspan=2, ipadx=5, ipady=5, padx=5, pady=5)
        # leftframe.pack(side=LEFT, fill=X, expand=True, ipadx=5, ipady=5, padx=5, pady=5)

        ''' Right Side Frame'''

        rightframe_ = tk.Frame(self)
        rightframe_.grid(row=0, column=1, rowspan=2, ipadx=5, ipady=5, padx=5, pady=5)
        # rightframe.pack(side=RIGHT, fill=X, expand=True, ipadx=5, ipady=5, padx=5, pady=5)

        ''' Bottom Frame'''

        bottomframe_ = tk.Frame(self)
        bottomframe_.grid(row=3, column=0, columnspan=2, ipadx=5, ipady=5, padx=5, pady=0)
        # bottomframe.pack(side=BOTTOM, fill=X, expand=True, ipadx=5, ipady=5, padx=5, pady=5)

        '''---------------------------------------------------------------------------'''

        # Combobox creation for available processes
        self.sv_cb_Avail_Jobs = tk.StringVar() 
        self.cb_Avail_Jobs = ttk.Combobox(leftframe_, textvariable = self.sv_cb_Avail_Jobs) 
        self.cb_Avail_Jobs.pack(fill=X, expand=True, ipadx=5, ipady=5)

        '''---------------------------------------------------------------------------'''

        # Refresh button
        self.btn_Clean_Names = tk.Button(rightframe_, height=1, text = "Refresh", command = self.refresh)      
        self.btn_Clean_Names.pack(fill=X, expand=True, ipadx=5, ipady=5)

        '''---------------------------------------------------------------------------'''

        # Interval spinbox
        self.iv_spn_spinval = tk.IntVar()
        self.spn_interval = ttk.Spinbox(leftframe_, increment=1, from_=1, to=100, textvariable=self.iv_spn_spinval)
        self.spn_interval.pack(fill=X, ipadx=5, ipady=5)

        '''---------------------------------------------------------------------------'''

        # Start button
        self.btn_Man_Save = tk.Button(rightframe_, height=1, text = "Start Saving", command = self.btn_start_toggle) 
        self.btn_Man_Save.pack(fill=X, expand=True, ipadx=5, ipady=5)

        '''---------------------------------------------------------------------------'''

        # Timeleft progressbar
        self.pb_time_left = ttk.Progressbar(bottomframe_, orient=HORIZONTAL, length=250)
        self.pb_time_left.pack(fill=Y, expand=True, ipadx=5, ipady=5)

        '''---------------------------------------------------------------------------'''

        # Timeleft label
        self.lbl_time_left = tk.Label(bottomframe_, text = "Time Left: 0 seconds")
        self.lbl_time_left.pack(side=LEFT, ipadx=5, ipady=5) 

        # set traces / callbacks
        self.traces()
        # Initial info grab
        self.refresh()
        # Run function once. Done because self.sched_enabled would not toggle when set in __init__. why?
        self.first_cycle()
        # Start parallel loop.
        self.after(0, self.parallel_loop)

    def parallel_loop(self):
        ''' Internal TK loop '''
        loop_interval_ = int(250) # miliseconds
        # Run if scheduled taskes is enabled
        if self.sched_enabled:
            # Run scheduled tasks
            schedule.run_pending()
            # increment progress bar depending on loop interval  
            self.pb_time_left['value'] += (loop_interval_ / 1000)
            # Calculate percent complete
            percent_comp_ = int(round((self.pb_time_left['value']/self.interval_sec)*100, 0))
            # Update window title to show % comp
            self.title(f"Tia Auto Save - {percent_comp_}%")
            # Show Timeleft
            time_left_ = str('{:.2f}'.format(round((self.interval_sec - self.pb_time_left['value']) / 60, 2)))
            # Split time string at decimal
            time_split_ = time_left_.split(".")
            # Min left
            min_left_ = int(time_split_[0])
            # Seconds left
            sec_left_ = int(round((int(time_split_[1]) / 100) * 60, 0))
            # Update label with new info
            self.lbl_time_left.config(text=f"Next Save in {min_left_} minutes and {sec_left_} seconds.")
            # Resize window to show label
            self.geometry("280x165")
            # Set Button color and Text
            self.btn_Man_Save.configure(bg="red", 
                                        text = "Stop Saving") 
        else:
            # Reset timeleft
            self.pb_time_left['value'] = 0
            # Update window title to show % comp
            self.title(f"Tia Auto Save")
            # Update label
            self.lbl_time_left.config(text="Next Save in -- min and -- sec.")
            # Resize window to hide timeleft label
            self.geometry("280x140")
            # Set Button color and Text
            self.btn_Man_Save.configure(bg="green", text = "Start Saving")
        
        # re-execute after set MS delay (500 = 5 ms)
        self.after(loop_interval_, self.parallel_loop)

    def first_cycle(self):
        '''For whatever reason, these items do not work when in __init__'''
        # Start with scheduled tasks disabled
        self.sched_enabled = False
        # Set initial / Default save interval
        self.iv_spn_spinval.set(int(5))
        
    def save_project(self):
        # Get current time
        now_ = datetime.now()
        # format current time
        current_time_ = now_.strftime("%H:%M:%S.%f")
        # reset progress bar
        self.pb_time_left['value'] = 0
        # Attemt save
        try:
            self.myproject.Save()
            print(current_time_, "File Saved...")
        except Exception as e:
            if str(type(e)) == str("<class 'Siemens.Engineering.EngineeringTargetInvocationException'>"):
                print(current_time_, 
                        "Save Failed: Processes can not be saved while ONLINE!\n",
                        "--------------------------------------------------------\n", 
                        e, 
                        "\n--------------------------------------------------------\n")
                messagebox.showwarning("TIA Portal Auto Save", "For auto save to work, TIA Portal can not be online with a PLC or PLCSIM! Go offline and click OK.")
                # self.sched_enabled = 0
            else:
                print(current_time_, 
                        "Save Failed...\n", 
                        "--------------------------------------------------------\n", 
                        e, 
                        "\n--------------------------------------------------------\n")
        
    def traces(self):
        # Execute if spinbox intvar changes
        self.iv_spn_spinval.trace('w', self.set_save_interval)
        # Execute if combobox stringvar changes
        self.sv_cb_Avail_Jobs.trace('w', self.set_job_selection)

    def btn_start_toggle(self):
        # invert bit when button is pressed
        self.sched_enabled = not self.sched_enabled
        print("self.sched_enabled", self.sched_enabled)

    def get_processes(self):
        ''' Get active TIA Portal processes'''
        # Get current active TIA Portal processes
        self.processes = tia.TiaPortal.GetProcesses()
        # Check if at least 1 process found
        if len(self.processes) > 0:
            self.process_found = True
        else:
            self.process_found = False
        # Print all active processes
        # for x in range(len(self.processes)):
        #     print(str(self.processes[x].ProjectPath))

    def get_job_info(self):
        ''' Get filenames and paths for all active processes'''
        # declare vars to be used
        self.jobs = []
        self.paths = []
        process_path_ = ''
        # If at leaste one TIA process is found
        if self.process_found:
            # Cycle through all process and append the job file names
            # and full windows file paths into individual lists
            for x in range(len(self.processes)):
                process_path_ = str(self.processes[x].ProjectPath)
                self.paths.append(process_path_.replace("\\","\\\\"))
                paths_split = process_path_.split("\\")
                self.jobs.append(paths_split[-1])
            # Add current process file names into combobox
            self.cb_Avail_Jobs['values'] = self.jobs
        else:
            # Display message in combobox
            self.cb_Avail_Jobs['values'] = ['No Processes Found', '']
        # set available jobs combobox to the first item
        self.cb_Avail_Jobs.current(0)

    def refresh(self):
        ''' look for new / current running processes '''
        self.get_processes()
        self.get_job_info()
        
    ''' CALLBACKS ------------------------------------------------------------'''

    def set_job_selection(self, *args):
        '''Callback: Executed when process dropdown has changed'''
        # If a TIA process is running
        if self.process_found:
            # Get combobox selection
            self.selected_job = self.sv_cb_Avail_Jobs.get()
            # Get index of cb selection
            self.selected_job_index = int(self.jobs.index(self.selected_job))
            # Show selected job and location
            print("\nSelected Job: ", self.selected_job)
            print("Selected Job Loc: ", self.paths[self.selected_job_index])
            # Stop running any currently running scheduled tasks
            self.sched_enabled = False
            # Connect to selected process
            self.mytia = self.processes[self.selected_job_index].Attach()
            self.myproject = self.mytia.Projects[0]

    def set_save_interval(self, *args):
        '''Callback: Executed when spinbox intvar is changed'''
        # Get spinbox value
        interval_ = int(self.iv_spn_spinval.get())
        # Set Min limit for interval
        if interval_ < 1:
            self.iv_spn_spinval.set(int(1))
        # Convert to seconds (used for % complete)
        self.interval_sec =  interval_ * 60
        # Set progress bar scale
        self.pb_time_left.config(maximum = self.interval_sec)
        # Clear progress bar value
        self.pb_time_left['value'] = 0
        # Clear existing scheduled tasks
        schedule.clear()
        # Schedule task
        schedule.every(interval_).minutes.do(self.save_project)

if __name__ == "__main__":
    app = tia_connect()
    app.mainloop()
