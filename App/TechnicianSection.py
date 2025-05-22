import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime
import tkinter.messagebox as messagebox

DB_PATH = 'App/Database/gui_database.db'

class ManageSensors(ctk.CTkFrame): 
    def __init__(self, master, controller, user_id, sensor_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.master = master
        self.user_id = user_id  
        self.sensor_id = sensor_id
        self.sensor_data = self.get_sensor(sensor_id)

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
            ("wharehouse", "entry"),
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



        # === Patient Name ===
        patient_row = len(field_info)
        patient_label = ctk.CTkLabel(form_frame, text="Assign to patient (by name):")
        patient_label.grid(row=patient_row, column=0, sticky="e", padx=5, pady=5)

        current_patient_name = self.sensor_data["patient"] if self.sensor_data and self.sensor_data["patient"] else ""
        self.patient_entry = ctk.CTkEntry(form_frame, placeholder_text=str(current_patient_name))
        self.patient_entry.grid(row=patient_row, column=1, sticky="ew", padx=5, pady=5)


        # === Submit Button ===
        self.submit_btn = ctk.CTkButton(parent, text="Update Sensor", command=self.submit)
        self.submit_btn.grid(row=2, column=0, pady=(10,500))

        availability_value = self.fields.get("availability")
        if availability_value and availability_value.get() == "U":
            self.see_report_btn = ctk.CTkButton(
                    parent,
                    text="➕ See report",
                    fg_color="#38a3a5",
                    hover_color="#57cc99",
                    #command=self.see_report
            )
        self.see_report_btn.grid(row=2, column=1, pady=(10,500))
    def submit(self):
        availability = self.fields["availability"].get().strip().upper() or self.sensor_data["availability"]
        status = self.fields["Status"].get().strip() or self.sensor_data["Status"]
        patient_name = self.patient_entry.get().strip()

        patient_id = self.sensor_data["patient"] if self.sensor_data else None

        if availability == 'U':
            if not patient_name:
                messagebox.showerror("Error", "Availability 'U' requires a patient name.")
                return

            patient = self.get_patient_by_name(patient_name)
            if not patient:
                messagebox.showerror("Error", f"No patient found with name '{patient_name}'.")
                return

            signal_acquired = self.fields["Signal_Acquired"].get().strip() or self.sensor_data["Signal_Acquired"]
            if not self.has_valid_prescription(patient["user_id"], signal_acquired):
                messagebox.showerror("Error", "Patient does not have a valid prescription for this sensor.")
                return

            patient_id = patient["user_id"]

        # Update the sensor
        self.update_sensor(self.sensor_id, availability, status, patient_id)
        messagebox.showinfo("Success", "Sensor updated successfully.")
        self.controller.show_internal_page("main")

    @staticmethod
    def get_sensor(sensor_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        sensor = conn.execute("SELECT * FROM Sensors WHERE Code_device = ?", (sensor_id,)).fetchone()
        conn.close()
        return sensor

    @staticmethod
    def get_patient_by_name(name):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        patient = conn.execute("SELECT * FROM Patients WHERE name = ?", (name,)).fetchone()
        conn.close()
        return patient

    @staticmethod
    def has_valid_prescription(patient_id, signal_acquired):
        conn = sqlite3.connect(DB_PATH)
        result = conn.execute(
            "SELECT * FROM PrescriptionDevices WHERE patient = ? AND Signal_Acquired = ?",
            (patient_id, signal_acquired)
        ).fetchone()
        conn.close()
        return result is not None

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
            ("wharehouse", "entry"),
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
                "wharehouse": self.fields["wharehouse"].get(),
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
                    wharehouse, location
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(values.values()))

            self.conn.commit()
            messagebox.showinfo("Success", "Sensor added successfully.")
            self.controller.show_internal_page("main")  # Update this with your actual return method

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class Main(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        # Scrollable frame for appointments
        scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
        scrollable_frame.pack(pady=10, padx=0, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.maintecgui(scrollable_frame, user_id)

    def maintecgui(self, parent, user_id):

        # === Header Title ===
        title_label = ctk.CTkLabel(parent, text="Welcome technician!", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))

        try:
            profile_img = ctk.CTkImage(light_image=Image.open("App/technicianprofile.jpg"), size=(50, 50))
            profile_pic = ctk.CTkLabel(parent, image=profile_img, text="")
            profile_pic.grid(row=0, column=0, pady=(20, 10))
        except:
            pass

        ctk.CTkLabel(parent, text="Sensors 🛠", font=ctk.CTkFont(size=22, weight="bold")).grid(row=1, column=0, columnspan=3, pady=(10, 10))

        # FILTERING 
        # === Filter Controls ===
        filter_frame = ctk.CTkFrame(parent, fg_color="white")
        filter_frame.grid(row=2, column=0, columnspan=6, pady=(10, 10))

        # Availability Filter
        self.avail_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Availability:").grid(row=0, column=0, padx=5)
        avail_menu = ctk.CTkOptionMenu(filter_frame, variable=self.avail_filter_var, 
                                       fg_color = "#38a3a5", button_color="#57cc99", button_hover_color="#38a3a5", 
                                       values=["All", "A", "U", "M"])
        avail_menu.grid(row = 0, column=1, padx=5)

        # Signal Filter
        self.signal_filter_var = ctk.StringVar(value="All")
        ctk.CTkLabel(filter_frame, text="Signal:").grid(row=0, column=2, padx=5)
        self.cursor.execute("SELECT DISTINCT Signal_Acquired FROM Sensors")
        signal_options = ["All"] + [row[0] for row in self.cursor.fetchall()]
        signal_menu = ctk.CTkOptionMenu(filter_frame, variable=self.signal_filter_var,
                                        fg_color = "#38a3a5", button_color="#57cc99", button_hover_color="#38a3a5", 
                                        values=signal_options)
        signal_menu.grid(row=0, column=3, padx=5)

        # Apply Button
        apply_button = ctk.CTkButton(filter_frame, 
                                    text="Apply Filters", 
                                    fg_color="#38a3a5",
                                    hover_color="#57cc99",         
                                    command=lambda: self.display_sensors(parent))
        apply_button.grid(row=0, column=4, padx=10)

        # === Table Headers ===
        headers = ["ID", "Name", "Signal", "Availability", "Status"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(parent, text=header, font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            header_label.grid(row=3, column=col, padx=5, pady=5, sticky="ew")

        # === Fetch Sensor Data ===
        self.cursor.execute("SELECT Code_device, Name, Signal_Acquired, availability, Status FROM Sensors")
        sensors = self.cursor.fetchall()

        # === Display Each Sensor as a Row ===
        for i, sensor in enumerate(sensors):
            for j, value in enumerate(sensor):
                if j == 0:  # Make sensor ID clickable
                    btn = ctk.CTkButton(
                        parent,
                        text=str(value),
                        fg_color="white",
                        text_color="black",
                        hover_color="#d3d3d3",
                        corner_radius=0,
                        font=ctk.CTkFont(size=12),
                        command=lambda sid=value: self.controller.show_manage_sensor_page(sid, user_id)
                    )
                    btn.grid(row=i+4, column=j, padx=5, pady=2, sticky="ew")
                else:
                    cell = ctk.CTkLabel(parent, text=str(value), font=ctk.CTkFont(size=12), anchor="w")
                    cell.grid(row=i+4, column=j, padx=5, pady=2, sticky="ew")

        ctk.CTkButton(
            master = parent,
            text="🛠 Add Sensor", # this would be to add new sensors or remove them
            width=180,
            corner_radius=10,
            fg_color="#38a3a5",
            hover_color="#57cc99", 
            text_color="white",
            font=ctk.CTkFont(size=14),
            command=lambda: self.controller.show_internal_page("addsensors")
        ).grid(row=1000, column=0, columnspan=3, pady=(30, 10))


    def display_sensors(self, parent):
        # Remove existing sensor rows
        for widget in parent.winfo_children():
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)) and widget.grid_info().get("row", 0) >= 3 and widget.grid_info().get("row", 0) <= 100:
                widget.destroy()

        # Header row
        headers = ["ID", "Name", "Signal", "Availability", "Status"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(parent, text=header, font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            header_label.grid(row=3, column=col, padx=5, pady=5, sticky="ew")

        # Filters
        availability = self.avail_filter_var.get()
        signal = self.signal_filter_var.get()

        query = "SELECT Code_device, Name, Signal_Acquired, availability, Status FROM Sensors WHERE 1=1"
        params = []

        if availability != "All":
            query += " AND availability = ?"
            params.append(availability)

        if signal != "All":
            query += " AND Signal_Acquired = ?"
            params.append(signal)

        self.cursor.execute(query, params)
        sensors = self.cursor.fetchall()

        # Display rows
        for i, sensor in enumerate(sensors):
            for j, value in enumerate(sensor):
                if j == 0:  # Make sensor ID clickable
                    btn = ctk.CTkButton(
                        parent,
                        text=str(value),
                        fg_color="white",
                        text_color="black",
                        hover_color="#d3d3d3",
                        corner_radius=0,
                        font=ctk.CTkFont(size=12),
                        command=lambda sid=value: self.controller.show_manage_sensor_page(sid, user_id)
                    )
                    btn.grid(row=i+4, column=j, padx=5, pady=2, sticky="ew")
                else:
                    cell = ctk.CTkLabel(parent, text=str(value), font=ctk.CTkFont(size=12), anchor="w")
                    cell.grid(row=i+4, column=j, padx=5, pady=2, sticky="ew")


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
         
        # Hide all initially -> not necessary
        for page in self.pages.values():
            page.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            page.grid_forget()

        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()    
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def show_manage_sensor_page(self, sensor_id, user_id):
        manage_page = ManageSensors(self, self, user_id, sensor_id)
        self.pages["manage"] = manage_page
        manage_page.grid(row=0, column=0, sticky="nsew")
        manage_page.tkraise()
