import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime
import tkinter.messagebox as messagebox

import os
import subprocess
import sys
DB_PATH = "App/Database/gui_database.db"


def logout():
    app_path = os.path.join(os.path.dirname(__file__), "App.py")
    python = sys.executable
    subprocess.Popen([python, app_path])  # Launch App.py as new process
    sys.exit()  # Exit current GUI app

import customtkinter as ctk
import sqlite3
from tkinter import messagebox

# class SeeReport(ctk.CTkFrame):
#     def __init__(self, master, sensor_id, user_id):
#         super().__init__(master, fg_color="white")
#         self.sensor_id = sensor_id
#         self.user_id = user_id
#         self.master = master

#         self.grid(row=0, column=0, sticky="nsew")
#         self.grid_configure(padx=20, pady=20)
#         self.columnconfigure(0, weight=1)
#         self.rowconfigure(2, weight=1)

#         # Back Button
#         back_button = ctk.CTkButton(
#             master=self,
#             text="← Back",
#             width=60,
#             height=30,
#             font=ctk.CTkFont(size=14),
#             fg_color="#57c2a8",
#             hover_color="#034172",
#             command=lambda: self.show_manage_sensor_page(sensor_id=self.sensor_id, user_id=self.user_id)
#         )
#         back_button.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(10, 10))

#         # Title
#         self.title_label = ctk.CTkLabel(self, text=f"Sensor Report for ID {sensor_id}", font=("Arial", 20))
#         self.title_label.grid(row=1, column=0, pady=(0, 10), sticky="n")

#         # Scrollable frame
#         self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Reports")
#         self.scroll_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 10))

#         # Load data
#         self.load_data()

#     def load_data(self):
#         try:
#             conn = sqlite3.connect("your_database.db")  # Replace with your actual database
#             c = conn.cursor()

#             c.execute("""
#                 SELECT squest_id, patient, sensor_id, date, created_at, malfunction 
#                 FROM SensorQuestionnaire 
#                 WHERE sensor_id = ?
#                 ORDER BY created_at DESC
#             """, (self.sensor_id,))
#             rows = c.fetchall()

#             if not rows:
#                 no_data_label = ctk.CTkLabel(self.scroll_frame, text="No reports found for this sensor.", font=("Arial", 14))
#                 no_data_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
#                 return

#             for i, row in enumerate(rows):
#                 report_text = (
#                     f"Report ID: {row[0]}\n"
#                     f"Patient ID: {row[1]}\n"
#                     f"Sensor ID: {row[2]}\n"
#                     f"Date: {row[3]}\n"
#                     f"Created At: {row[4]}\n"
#                     f"Malfunction: {row[5]}\n"
#                 )
#                 report_box = ctk.CTkTextbox(self.scroll_frame, height=120, width=600)
#                 report_box.insert("0.0", report_text)
#                 report_box.configure(state="disabled")
#                 report_box.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

#             conn.close()

#         except sqlite3.Error as e:
#             messagebox.showerror("Database Error", str(e))

class ManageSensors(ctk.CTkFrame): 
    def __init__(self, master, controller, user_id, sensor_id, main_page):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.master = master
        self.user_id = user_id  
        self.sensor_id = sensor_id
        self.sensor_data = self.get_sensor(sensor_id)
        self.main_page = main_page

        scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")        
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.addgui(scrollable_frame)

    def addgui(self, parent):
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(parent, text="Update this sensor:", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10), sticky="w")

        back_button = ctk.CTkButton(
            master=parent,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command=lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # === Fields Grid ===
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)

        self.fields = {}
        field_info = [
            ("Name", "entry"),
            ("Signal_Acquired", "entry"),
            ("availability", "dropdown", ["A", "U", "M"]),
            ("model", "entry"),
            ("description", "entry"),
            ("Status", "entry"),
            ("assigned_at_time", "entry", "YYYY-MM-DD HH:MM"),
            ("patient", "entry"),
            ("PrescriptionDevices_id", "entry"),
            ("warehouse", "entry"),
            ("location", "entry")
        ]

        for i, (label_text, field_type, *extra) in enumerate(field_info):
            ctk.CTkLabel(form_frame, text=label_text + ":", anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=5)

            if self.sensor_data and label_text in self.sensor_data.keys():
                current_value = self.sensor_data[label_text]
            else:
                current_value = ""

            if field_type == "entry":
                entry = ctk.CTkEntry(form_frame, width=250, placeholder_text=str(current_value))
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.fields[label_text] = entry
            elif field_type == "dropdown":
                values = extra[0]
                selected = str(current_value) if current_value in values else values[0]
                var = ctk.StringVar(value=selected)
                dropdown = ctk.CTkOptionMenu(form_frame, values=values, variable=var)
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                self.fields[label_text] = var

        # === Submit Button ===
        self.submit_btn = ctk.CTkButton(parent, text="Update Sensor", command=self.submit)
        self.submit_btn.grid(row=2, column=1, pady=(10,500))

        availability_value = self.fields.get("availability")
        if availability_value and availability_value.get() == "U":
            self.see_report_btn = ctk.CTkButton(
                    parent,
                    text="➕ See report",
                    fg_color="#38a3a5",
                    hover_color="#57cc99",
                    command= lambda: self.controller.see_report(self.sensor_id, self.user_id)
            )
            self.see_report_btn.grid(row=2, column=0, pady=(10,500))
    
   

    def submit(self):
        availability = self.fields["availability"].get().strip().upper() or self.sensor_data["availability"]
        status = self.fields["Status"].get().strip() or self.sensor_data["Status"]
        patient_id = self.fields["patient"].get().strip() if self.fields["patient"] else None
        # Maybe add a check to see if patient was modified, else use None

        if availability == 'U':
            if not patient_id:
                messagebox.showerror("Error", "Availability 'U' requires a patient.")
                return

            patient = self.get_patient_by_user(patient_id)
            
            if not patient:
                messagebox.showerror("Error", f"No patient found with ID '{patient_id}'.")
                return

            signal_acquired = self.fields["Signal_Acquired"].get().strip() or self.sensor_data["Signal_Acquired"]
            if self.has_valid_prescription(patient["user_id"], signal_acquired) is None:
                messagebox.showerror("Error", "Patient does not have a valid prescription for this sensor.")
                return
            prescription_id = self.has_valid_prescription(patient["user_id"], signal_acquired)

            self.fields["PrescriptionDevices_id"] = prescription_id 

        # Update the sensor
        self.update_sensor(self.sensor_id, availability, status, patient_id)
        messagebox.showinfo("Success", "Sensor updated successfully.")
        self.controller.pages["main"].display_sensors(self.controller.pages["main"].scrollable_frame)
      

    @staticmethod
    def get_sensor(sensor_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        sensor = conn.execute("SELECT * FROM Sensors WHERE Code_device = ?", (sensor_id,)).fetchone()
        conn.close()
        return sensor

    @staticmethod
    def get_patient_by_user(patient_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        patient = conn.execute("SELECT * FROM Patients WHERE user_id= ?", (patient_id,)).fetchone()
        conn.close()
        return patient

    @staticmethod
    def has_valid_prescription(patient_id, signal_acquired):
        conn = sqlite3.connect(DB_PATH)
        prescription_id = conn.execute(
            "SELECT prescription_id FROM PrescriptionDevices WHERE patient = ? AND sensor_type = ?",
            (patient_id, signal_acquired)
        ).fetchone()
        conn.close()
        return prescription_id

    @staticmethod
    def update_sensor(sensor_id, availability, status, patient_id):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE Sensors 
            SET availability = ?, Status = ?, patient = ?, assigned_at_time = ?
            WHERE Code_device = ?
        """, (availability, status, patient_id, datetime.datetime.now(), sensor_id))
        conn.commit()
        conn.close()

    def set_sensor_id(self, sensor_id):
        self.sensor_id = sensor_id
        print(f"Sensor ID set to: {self.sensor_id}")

class AddSensors(ctk.CTkFrame):  
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.master = master
        self.user_id = user_id  
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()      
        scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.addgui(scrollable_frame)

    def addgui(self, parent):
        parent.grid_columnconfigure(0, weight=0)  # Back button column
        parent.grid_columnconfigure(1, weight=1)  # Main content column

        title_label = ctk.CTkLabel(parent, text="New Sensor's Informations:", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))

        # === Back Button in Top-Left ===
        back_button = ctk.CTkButton(
            master=parent,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command= lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        title_label = ctk.CTkLabel(parent, text="New Sensor's Informations:", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))

        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)  # Make input column expand

        # Input Fields
        self.fields = {}

        field_info = [
            ("Name", "entry"),
            ("Signal_Acquired", "entry"),
            ("availability", "dropdown", ["A", "U", "M"]),
            ("model", "entry"),
            ("description", "entry"),
            ("Status", "entry"),
            ("assigned_at_time", "entry", "YYYY-MM-DD HH:MM"),
            ("patient", "entry"),
            ("PrescriptionDevices_id", "entry"),
            ("warehouse", "entry"),
            ("location", "entry")
        ]

        for i, (label_text, field_type, *extra) in enumerate(field_info):
            ctk.CTkLabel(form_frame, text=label_text + ":", anchor="w").grid(row=i, column=0, sticky="w", padx=5, pady=5)

            if field_type == "entry":
                entry = ctk.CTkEntry(form_frame, width=250)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.fields[label_text] = entry
            elif field_type == "dropdown":
                values = extra[0]
                var = ctk.StringVar(value=values[0])
                dropdown = ctk.CTkOptionMenu(form_frame, values=values, variable=var)
                dropdown.grid(row=i, column=1, padx=5, pady=5)
                self.fields[label_text] = var

        # Submit Button
        submit_btn = ctk.CTkButton(
            parent, 
            text="➕ Add Sensor", 
            fg_color="#38a3a5", 
            hover_color="#57cc99", 
            command=self.submit_form
        )
        submit_btn.grid(row=12, column=0, columnspan=2, pady=(20, 5000))
        parent.update_idletasks()

    def submit_form(self):
        try:
            values = {
                "Name": self.fields["Name"].get(),
                "Signal_Acquired": self.fields["Signal_Acquired"].get(),
                "availability": self.fields["availability"].get(),
                "model": self.fields["model"].get(),
                "description": self.fields["description"].get(),
                "Status": self.fields["Status"].get(),
                "assigned_at_time": self.fields["assigned_at_time"].get(),
                "patient": self.fields["patient"].get(),
                "PrescriptionDevices_id": self.fields["PrescriptionDevices_id"].get(),
                "warehouse": self.fields["warehouse"].get(),
                "location": self.fields["location"].get()
            }

            # Basic validation
            if not values["Name"] or not values["Signal_Acquired"]:
                messagebox.showerror("Error", "Name and Signal_Acquired are required.")
                return

            # Optional: Validate datetime format
            if values["assigned_at_time"]:
                try:
                    datetime.strptime(values["assigned_at_time"], "%Y-%m-%d %H:%M")
                except ValueError:
                    messagebox.showerror("Error", "assigned_at_time must be in 'YYYY-MM-DD HH:MM' format.")
                    return

            self.cursor.execute("""
                INSERT INTO Sensors (
                    Name, Signal_Acquired, availability, model, description,
                    Status, assigned_at_time, patient, PrescriptionDevices_id,
                    warehouse, location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(values.values()))

            self.conn.commit()
            messagebox.showinfo("Success", "Sensor added successfully.")
            self.controller.show_internal_page("main") 

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class Main(ctk.CTkFrame):
    def toggle_manage_mode(self, parent):
        self.manage_mode = not self.manage_mode
        self.manage_btn.configure(
            text="✅ Exit Manage Mode" if self.manage_mode else "🛠 Manage Sensors"
        )
        self.display_sensors(parent)

    def delete_sensor(self, sensor_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this sensor?"):
            self.cursor.execute("DELETE FROM Sensors WHERE Code_device = ?", (sensor_id,))
            self.conn.commit()

    def display_sensors(self, parent):
        for i in range(5):
            parent.grid_columnconfigure(i, weight=1, uniform="sensor_cols")
        parent.grid_columnconfigure(4, weight=0, minsize=50)  

        # Remove old sensor rows (row >= 3)
        for widget in parent.winfo_children():
            info = widget.grid_info()
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)) and info.get("row", 0) >= 3 and info.get("row", 0) <= 100:
                widget.destroy()

        # Header row
        headers = ["ID", "Name", "Signal", "Availability"]
        if self.manage_mode:
            headers.append("Delete")
        if not self.manage_mode:
            headers.append("Status")

        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(parent, text=header, font=ctk.CTkFont(size=14, weight="bold"))
            if col == 0:
                sticky = "ew"
            else:
                sticky = "w"
            header_label.grid(row=3, column=col, padx=5, pady=5, sticky= sticky)

        # Apply filters
        availability = self.avail_filter_var.get()
        signal = self.signal_filter_var.get()

        query = "SELECT Code_device, Name, Signal_Acquired, availability FROM Sensors WHERE 1=1"
        params = []
        if not self.manage_mode:
            query = "SELECT Code_device, Name, Signal_Acquired, availability, Status FROM Sensors WHERE 1=1"

        if availability != "All":
            query += " AND availability = ?"
            params.append(availability)

        if signal != "All":
            query += " AND Signal_Acquired = ?"
            params.append(signal)

        self.cursor.execute(query, params)
        sensors = self.cursor.fetchall()

        # Sensor data rows
        for i, sensor in enumerate(sensors):
            for j, value in enumerate(sensor):
                if j == 0:
                    btn = ctk.CTkButton(
                        parent,
                        text=str(value),
                        fg_color="white",
                        text_color="black",
                        hover_color="#d3d3d3",
                        corner_radius=0,
                        font=ctk.CTkFont(size=12),
                        command=lambda sid=value: self.controller.show_manage_sensor_page(sid, self.user_id)
                    )
                    btn.grid(row=i+4, column=j, padx=5, pady=2, sticky="w")
                else:
                    cell = ctk.CTkLabel(parent, text=str(value), font=ctk.CTkFont(size=12), anchor="w")
                    cell.grid(row=i+4, column=j, padx=5, pady=2, sticky="w")

            if self.manage_mode:
                del_button = ctk.CTkButton(
                    parent,
                    text="❌",
                    width=30,
                    height=30,
                    font=ctk.CTkFont(size=14),
                    fg_color="#ff6b6b",
                    hover_color="#ff4d4d",
                    text_color="white",
                    command=lambda sen=sensor[0]: self.delete_sensor(sen)
                )
                del_button.grid(row=i+4, column=4, sticky="w", padx=(0, 5))

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.manage_mode = False
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
        self.scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)

        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.maintecgui(self.scrollable_frame, user_id)

    def maintecgui(self, parent, user_id):

        try:
            profile_img = ctk.CTkImage(light_image=Image.open("App/technicianprofile.jpg"), size=(50, 50))
            profile_pic = ctk.CTkLabel(parent, image=profile_img, text="")
            profile_pic.grid(row=0, column=0, pady=(20, 10), padx=(10, 5))
        except:
            pass

        title_label = ctk.CTkLabel(parent, text="Welcome technician!", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, columnspan=3, pady=(20, 10), sticky="w")

        #        # === Header Title ===
        # query = """
        #     SELECT 
        #         T.Name
        #     FROM Technicians T
        #     WHERE T.user_id = ? 
        # """
        # self.cursor.execute(query, (user_id,))
        # result = self.cursor.fetchone()
        # name = result[0] if result else "User"

        # title_label = ctk.CTkLabel(self, text=f"Welcome, {name}", font=ctk.CTkFont(size=22, weight="bold"))
        # title_label.grid(row=0, column=0, pady=(20, 10))

        # # === Profile Picture ===
        # query = """
        #     SELECT 
        #         T.profilepic
        #     FROM Technicians T
        #     WHERE T.user_id = ? 
        # """
        # self.cursor.execute(query, (user_id,))
        # result = self.cursor.fetchone()
        # path = result[0] if result else None

        # if path:
        #     try:
        #         profile_img = ctk.CTkImage(light_image=Image.open(path), size=(80, 80))
        #         profile_pic = ctk.CTkLabel(self, image=profile_img, text="")
        #         profile_pic.grid(row=1, column=0, pady=(0, 20))
        #     except Exception as e:
        #         print(f"Failed to load profile picture: {e}")



        # === Bottom Menu ===
        menu_bar = ctk.CTkFrame(parent, fg_color="transparent")
        menu_bar.grid(row=0, column=3, pady=20, sticky="e")

        menu_button = ctk.CTkButton(
            master=menu_bar,
            text="↪ Logout",
            width=100,
            height=35,
            fg_color="#38a3a5",
            hover_color="#57cc99",
            font=ctk.CTkFont(size=14),
            command= logout
        )
        menu_button.pack()

        ctk.CTkLabel(parent, text="🛠 List of Sensors:", font=ctk.CTkFont(size=22, weight="bold"))\
            .grid(row=1, column=0, columnspan=3, padx = 30, pady=(10, 10), sticky="w")

        filter_frame = ctk.CTkFrame(parent, fg_color="white")
        filter_frame.grid(row=2, column=0, columnspan=6, pady=(10, 10), sticky="ew")
        for i in range(5):
            filter_frame.grid_columnconfigure(i, weight=1)

        self.avail_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Availability:").grid(row=0, column=0, padx=5, sticky="ew")
        avail_menu = ctk.CTkOptionMenu(filter_frame, variable=self.avail_filter_var, width=120,
                                       fg_color="#38a3a5", button_color="#57cc99", button_hover_color="#38a3a5",
                                       values=["All", "A", "U", "M"])
        avail_menu.grid(row=0, column=1, padx=5)

        self.signal_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Signal:").grid(row=0, column=2, padx=5, sticky="ew")
        self.cursor.execute("SELECT DISTINCT Signal_Acquired FROM Sensors")
        signal_options = ["All"] + [row[0] for row in self.cursor.fetchall()]
        signal_menu = ctk.CTkOptionMenu(filter_frame, variable=self.signal_filter_var, width=120,
                                        fg_color="#38a3a5", button_color="#57cc99", button_hover_color="#38a3a5",
                                        values=signal_options)
        signal_menu.grid(row=0, column=3, padx=5)

        apply_button = ctk.CTkButton(filter_frame,
                                     text="Apply Filters",
                                     fg_color="#38a3a5",
                                     hover_color="#57cc99",
                                     width=70,
                                     command=lambda: self.display_sensors(parent))
        apply_button.grid(row=0, column=4, padx=10, sticky="w")

        self.display_sensors(parent)

        ctk.CTkButton(parent,
                      text="🛠 Add Sensor",
                      width=180,
                      corner_radius=10,
                      fg_color="#38a3a5",
                      hover_color="#57cc99",
                      text_color="white",
                      font=ctk.CTkFont(size=14),
                      command=lambda: self.controller.show_internal_page("addsensors")
                      ).grid(row=1000, column=0, columnspan=2, pady=(30, 10))

        self.manage_btn = ctk.CTkButton(parent,
                                        text="🛠 Manage Sensors",
                                        width=180,
                                        corner_radius=10,
                                        fg_color="#57cc99",
                                        hover_color="#38a3a5",
                                        text_color="white",
                                        font=ctk.CTkFont(size=14),
                                        command=lambda: self.toggle_manage_mode(parent))
        self.manage_btn.grid(row=1000, column=2, columnspan=2, pady=(30, 10))

# == Reference Page == #
class Home_tecPage(ctk.CTkFrame):

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.master = master
        self.user_id = user_id

        self.pages = {
            "main": Main(self, self, self.user_id),
            "addsensors": AddSensors(self, self, self.user_id),
            #"manage": ManageSensors(self, self, self.user_id, sensor_id = None),
        }
         
        for page in self.pages.values():
            page.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            page.grid_forget()

        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()    
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def show_manage_sensor_page(self, sensor_id, user_id):
        manage_page = ManageSensors(self, self, user_id, sensor_id, main_page=self.pages["main"])
        self.pages["manage"] = manage_page
        manage_page.grid(row=0, column=0, sticky="nsew")
        manage_page.tkraise()

    # def see_report(self, sensor_id, user_id):
    #     see_report = SeeReport(self, sensor_id, user_id)
    #     self.pages["see_report"] = see_report
    #     see_report.grid(row=0, column=0, sticky="nsew")
    #     see_report.tkraise()