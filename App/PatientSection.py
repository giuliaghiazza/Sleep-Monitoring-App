import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime
import tkinter.messagebox as messagebox
from DoctorSection import show_questionnaire_averages, show_pdf_in_new_window
import subprocess
import sys
import os

DB_PATH = "App/Database/gui_database.db"


def logout():
    app_path = os.path.join(os.path.dirname(__file__), "App.py")
    python = sys.executable
    subprocess.Popen([python, app_path])  # Launch App.py as new process
    sys.exit()  # Exit current GUI app

def get_questions():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT field_name, question_text, option_1, option_2, option_3, option_4, option_5 FROM QuestionDefinitions")
        return c.fetchall()

def last_submission_date(patient_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT date FROM PeriodicQuestionnaire WHERE patient_id = ? ORDER BY date DESC LIMIT 1", (patient_id,))
        row = c.fetchone()
        return datetime.datetime.strptime(row[0], "%Y-%m-%d") if row else None

def save_submission(patient_id, answers):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        fields = ", ".join(answers.keys())
        placeholders = ", ".join(["?"] * len(answers))
        values = list(answers.values())
        
        c.execute(f"""
            INSERT INTO PeriodicQuestionnaire (patient_id, date, {fields})
            VALUES (?, ?, {placeholders})
        """, [patient_id, datetime.datetime.now().date()] + values)
        conn.commit()

# Dictionary to hold pages
pages = {}
doc_avail_vect=None
#doc_sel='Select doctor'

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        self.inputs = {}  # To store input fields
        self.setup_gui()

    def setup_gui(self):
        # Back button 
        back_button = ctk.CTkButton(
            master=self,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            command=lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # Title
        title = ctk.CTkLabel(self, text="Update Your Information", font=("Arial", 20))
        title.grid(row=0, column=1, columnspan=2, pady=(20, 10))

        # Fetch current user data
        self.cursor.execute("SELECT Name, Surname, Codice_Fiscale, DoB, Gender, Age, City_of_Birth, Province_of_Birth, City_of_Recidency, Province_of_Recidency, CAP FROM Patients WHERE user_id=?", (self.user_id,))
        data = self.cursor.fetchone()

        fields = [
            ("Name", "First Name"),
            ("Surname", "Last Name"),
            ("Codice_Fiscale", "Tax Code (CF)"),
            ("DoB", "Date of Birth (YYYY-MM-DD)"),
            ("Gender", "Gender"),
            ("Age", "Age"),
            ("City_of_Birth", "City of Birth"),
            ("Province_of_Birth", "Province of Birth"),
            ("City_of_Recidency", "City of Residency"),
            ("Province_of_Recidency", "Province of Residency"),
            ("CAP", "Postal Code"),
        ]

        for idx, (field, label) in enumerate(fields):
            ctk.CTkLabel(self, text=label + ":", anchor="w").grid(row=idx + 1, column=0, padx=20, pady=5, sticky="w")
            entry = ctk.CTkEntry(self, width=200)
            if data:
                entry.insert(0, str(data[idx]) if data[idx] is not None else "")
            entry.grid(row=idx + 1, column=1, padx=20, pady=5, sticky="w")
            self.inputs[field] = entry

        # Submit Button
        submit_btn = ctk.CTkButton(self, text="Save Changes", command=self.save_changes)
        submit_btn.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

    def save_changes(self):
        updated_data = {field: entry.get() for field, entry in self.inputs.items()}

        try:
            # Input validation example for date and age
            datetime.datetime.strptime(updated_data["DoB"], "%Y-%m-%d")
            updated_data["Age"] = int(updated_data["Age"])
            updated_data["CAP"] = int(updated_data["CAP"])

            # Update statement
            self.cursor.execute("""
                UPDATE Patients SET
                    Name=?,
                    Surname=?,
                    Codice_Fiscale=?,
                    DoB=?,
                    Gender=?,
                    Age=?,
                    City_of_Birth=?,
                    Province_of_Birth=?,
                    City_of_Recidency=?,
                    Province_of_Recidency=?,
                    CAP=?
                WHERE user_id=?
            """, (*updated_data.values(), self.user_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Information updated successfully.")

        except ValueError:
            messagebox.showerror("Error", "Please ensure Age and Date of Birth are valid.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

class Main(ctk.CTkFrame):
    def toggle_manage_mode(self):
        self.manage_mode = not self.manage_mode
        self.manage_btn.configure(
            text="✅ Exit Manage Mode" if self.manage_mode else "🛠 Manage Appointments"
        )
        self.show_appointments(self.user_id)

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.setup_gui(user_id)
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        self.manage_mode = False 

    def setup_gui(self, user_id): 
        self.appointments_container = self

        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome, Mario!", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # === Profile Picture ===
        try:
           profile_img = ctk.CTkImage(light_image=Image.open("App/patientprofile.png"), size=(80, 80))
           profile_pic = ctk.CTkLabel(self, image=profile_img, text="")
           profile_pic.grid(row=1, column=0, pady=(0, 20))
        except:
           pass

        # === Buttons ===

        book_button = ctk.CTkButton(
            master=self,
            text="📅 Your Appointments",
            height=50,
            width=250,
            fg_color="#57cc99",
            hover_color="#38a3a5",
            font=ctk.CTkFont(size=16),
            command=lambda: self.show_appointments(user_id)
        )
        book_button.grid(row=2, column=1, padx=35, pady=10, sticky="ew")

        book_button = ctk.CTkButton(
            master=self,
            text="📅 Book Appointment",
            height=50,
            width=250,
            fg_color="#38a3a5",
            hover_color="#57cc99",
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("appointment")
        )
        book_button.grid(row=2, column=0, padx=35, pady=10, sticky="ew")

        data_button = ctk.CTkButton(
            master=self,
            text="📂 My Health Records",
            height=50,
            width=250,
            fg_color="#38a3a5",
            hover_color="#57cc99",
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("data")
        )
        data_button.grid(row=3, column=0, padx=35, pady=10, sticky="ew")

        emergency_button = ctk.CTkButton(
            master=self,
            text="🚨 Contact Page",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ff6666",
            hover_color="#ff4d4d",
            command=lambda: self.controller.show_internal_page("emergency")
        )
        emergency_button.grid(row=4, column=0, padx=35, pady=(30, 10), sticky="ew")

        # === Bottom Menu ===
        menu_bar = ctk.CTkFrame(self, fg_color="transparent")
        menu_bar.grid(row=5, column=0, pady=20)

        menu_button = ctk.CTkButton(
            master=menu_bar,
            text="🌣 Settings",
            width=100,
            height=35,
            fg_color="#57cc99",
            hover_color="#38a3a5",
            font=ctk.CTkFont(size=14),
            command=lambda: self.controller.show_internal_page("settings")
        )
        menu_button.pack()   

        # === Bottom Menu ===
        menu_bar = ctk.CTkFrame(self, fg_color="transparent")
        menu_bar.grid(row=101, column=1, pady=0, sticky = "e")

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
    
    def show_appointments(self, user_id):
        for widget in self.appointments_container.winfo_children():
            grid_info = widget.grid_info()
            if 3 <= int(grid_info.get("row", 0)) < 100 and int(grid_info.get("column", 0)) == 1:
                widget.destroy()

        today = "2025-05-29"
        query = f"""
            SELECT 
                A.slot_tempo, 
                A.visit_type,
                A.appointment_id,
                D.Name,
                D.Surname
            FROM Appointments A
            JOIN Doctors D ON A.doctor = D.user_id
            JOIN Patients P ON A.patient = P.user_id
            WHERE P.user_id = ? 
            AND A.slot_tempo >= ?
            """

        self.cursor.execute(query, (user_id, today))
        appointments = self.cursor.fetchall()

        if not appointments:
            ctk.CTkLabel(self.appointments_container, text= "There are no appointments scheduled!", text_color="#999").grid(row=3, column=0, columnspan=3, pady=20)
            return

        row = 3

        for appointment in appointments:
            time_str = appointment[0].split(' ')[1][:5]
            visit_type = appointment[1]
            self.cursor.execute("SELECT Visit FROM Visits WHERE visit_code = ?", (visit_type,))
            visit_name = self.cursor.fetchone()
            visit_name_str = visit_name[0] if visit_name else "Unknown"
            doctor_name = f"{appointment[3]} {appointment[4]}"
            appointment_id = appointment[2]

            if self.manage_mode:
                apt_text = f"{time_str} 🕒 | {doctor_name}"
            else:
                apt_text = f"{time_str} 🕒 | {doctor_name} | {visit_name_str}"


            apt_button = ctk.CTkButton(
                self.appointments_container,
                text=apt_text,
                width=200,
                height=40,
                font=ctk.CTkFont(size=14),
                corner_radius=10,
                fg_color= "#FFE5B4",
                hover_color= "#FFD6A5",
                text_color="#222",
                command=lambda vt=appointment_id: self.controller.show_internal_page("visit_details", vt)
            )
            apt_button.grid(row=row, column=1, columnspan=3, pady=5)

            if self.manage_mode:
                delete_btn = ctk.CTkButton(
                    self.appointments_container,
                    text="❌",
                    width=20,
                    height=20,
                    fg_color="#ff4d4d",
                    hover_color="#cc0000",
                    font=ctk.CTkFont(size=12),
                    command=lambda aid=appointment_id: self.delete_appointment(aid)
                )
                delete_btn.grid(row=row, column=1, padx=5, pady=5, sticky = "e")
            row += 1
        
        if appointments:
            book_button = ctk.CTkButton(
                master=self,
                text="🖊️ Compile your questionnaire!",
                height=50,
                width=250,
                fg_color="#57cc99",
                hover_color="#38a3a5",
                font=ctk.CTkFont(size=16),
                command=lambda: self.controller.show_internal_page("visitquest")
            )
            book_button.grid(row = row, column=1, padx=35, pady=0, sticky="ew")
            row += 1

        if appointments:
            self.manage_btn = ctk.CTkButton(
                master=self,
                text="🛠 Manage Appointments",
                height=30,
                width=70,
                fg_color="#57cc99",
                hover_color="#38a3a5",
                font=ctk.CTkFont(size=12),
                command=lambda: self.toggle_manage_mode()
            )
            self.manage_btn.grid(row = row, column=1, padx=35, pady=0)

    def delete_appointment(self, appointment_id):
        try:
            self.cursor.execute("DELETE FROM Appointments WHERE appointment_id = ?", (appointment_id,))
            self.conn.commit()
            messagebox.showinfo("Deleted", "Appointment deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete appointment: {e}")

        # Refresh the appointments list
        self.show_appointments(self.user_id)

class VisitQuestionnaire(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        self.quest_gui(self.user_id)

    def quest_gui(self, user_id):

        self.grid_columnconfigure(0, weight=0)  # Back button column
        self.grid_columnconfigure(1, weight=1)  # Main content column
        
        # === Back Button in Top-Left ===
        back_button = ctk.CTkButton(
            master = self,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            command= lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="📝 Visit Questionnaire", font=ctk.CTkFont(size=18))
        title_label.grid(row=0, column=1, pady=(20, 10))
        
        self.cursor.execute("""
            SELECT appointment_id FROM Appointments
            WHERE patient = ? AND visit_type = 1 AND quest = 0
            LIMIT 1
        """, (user_id,))
        result = self.cursor.fetchone()

        if result:
            self.appointment_id = result[0]
            self.build_form()
        else:
            title_label = ctk.CTkLabel(self, text="✅ No questionnaire to fill out.", font=ctk.CTkFont(size=16))
            title_label.grid(row = 1, column=  1, pady= (20,10))

    def build_form(self):
        title_label = ctk.CTkLabel(self, text="Fill out the questionnaire:.", font=ctk.CTkFont(size=16))
        title_label.grid(row = 1, column = 1, pady= (20,10))
        
        # === Questionnaire Fields ===
        self.entries = {}

        fields = [
            ("Pathologies", "pathologies"),
            ("Medication", "medication"),
            ("Physical Activity", "physicalactivity"),
            ("Sleep Hours", "sleephours"),
            ("Sleep Quality", "sleepquality"),
            ("Diet", "diet"),
            ("Tobacco Use", "tobacco"),
            ("Alcohol Use", "alcohol"),
            ("Stress Level", "stress"),
            ("Notes", "notes")
        ]

        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(self, text=label).grid(row=i+1, column=0, sticky="e", padx=10, pady=5)
            entry = ctk.CTkEntry(self, width=300)
            entry.grid(row=i+1, column=1, sticky="w", padx=10, pady=5)
            self.entries[key] = entry

        # === Save Button ===
        save_button = ctk.CTkButton(self, text="💾 Save", command= self.save_questionnaire)
        save_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)

    def save_questionnaire(self):
        print("Saving questionnaire...")
        data = {key: entry.get() for key, entry in self.entries.items()}
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Insert into the database
        self.cursor.execute("""
            INSERT INTO VisitQuestionnaire(
                appointment_id, pathologies, medication, physicalactivity, sleephours,
                sleepquality, diet, tobacco, alcohol, stress, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.appointment_id,
            data["pathologies"],
            data["medication"],
            data["physicalactivity"],
            data["sleephours"],
            data["sleepquality"],
            data["diet"],
            data["tobacco"],
            data["alcohol"],
            data["stress"],
            data["notes"],
            created_at
        ))

        self.cursor.execute("""
            UPDATE Appointments SET quest = 1 WHERE appointment_id = ?
        """, (self.appointment_id,))
        
        self.conn.commit()
        messagebox.showinfo("Success", "✅ Questionnaire saved successfully!")
        self.controller.show_internal_page("main")  # Redirect to main page after saving

class AppointmentPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.setup_gui(self.user_id)

    def setup_gui(self, user_id):
        self.grid_columnconfigure(0, weight=1)  # Back button column
        self.grid_columnconfigure(1, weight=1)  # Main content column
        
        scrollable_frame_tot1 = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame_tot1.grid(pady=20, padx=10)       #, fill="both", expand=True
        scrollable_frame_tot1.grid_columnconfigure((0, 1), weight=1)

        # === Back Button in Top-Left ===
        back_button = ctk.CTkButton(
            master = scrollable_frame_tot1,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            command= lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="e")
    
        # === Header Title ===
        title_label = ctk.CTkLabel(scrollable_frame_tot1, text="📅 Book Appointment Page", font=ctk.CTkFont(size=18))
        title_label.grid(row=0, column=1, pady=(20, 10))
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        self.frame = ctk.CTkFrame(scrollable_frame_tot1, fg_color="white")
        self.frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.frame.grid_columnconfigure(1, weight=1)
        
        #self.cursor.execute('SELECT DISTINCT doctor FROM appointment WHERE patient=?', (user,)) #user da passare
        #self.selected_value = None
        selected_value = ctk.StringVar(value=None)
        self.selected_index=None
        self.selected_index1=None
        self.selected_index2=None
        
        data_del_lable=ctk.CTkLabel(self.frame, 
                                text='Filter for date', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        data_del_lable.grid(row=0, column=0, padx=20, pady=10)
        self.cursor.execute('SELECT DATE(slot_tempo) AS date_only FROM Appointments')
        hours=self.cursor.fetchall()
        self.combobox_1 = ctk.CTkOptionMenu(self.frame,
                                        values = [str(hour[0]) for hour in hours],
                                        #command=self.save_selection
                                        variable=selected_value)
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        #self.combobox_1.set("")

        if selected_value is None:
            self.cursor.execute('SELECT DISTINCT slot_tempo FROM Appointments WHERE dispo=1')
            n_availability_vect=self.cursor.fetchall()
            n_availability= len(n_availability_vect)
        else:
            self.cursor.execute('SELECT DISTINCT slot_tempo FROM Appointments WHERE dispo=1 AND DATE(slot_tempo)=?', (selected_value.get(),))
            n_availability_vect=self.cursor.fetchall()
            n_availability= len(n_availability_vect)

        #tab prenotazione
        #self.tabview = ctk.CTkTabview(self, width=250)
        #self.tabview.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        #self.tabview.add("Availability")
        #self.tabview.add("Doctor")
        #self.tabview.add("Submit")
        #self.tabview.tab("Availability").grid_columnconfigure(0, weight=1)
        #self.tabview.tab("Doctor").grid_columnconfigure(0, weight=1)

        #self.scrollable_frame = ctk.CTkScrollableFrame(self.tabview.tab("Availability"), label_text="Select time slot")
        #self.scrollable_frame.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        #self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_radiobut = []
        self.radio_var = ctk.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(self.frame, text="Available slots")
        for i in range(n_availability):
            slot_text=n_availability_vect[i][0]
            radio_button = ctk.CTkRadioButton(self.frame, variable=self.radio_var, value=i, text=slot_text)
            radio_button.grid(row=i+2, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_radiobut.append(radio_button)
        slot_sel= self.get_selected_text()

     
        self.frame1 = ctk.CTkFrame(scrollable_frame_tot1, fg_color="white")
        self.frame1.grid(row=2, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.frame1.grid_columnconfigure(1, weight=1)

        selected_doc=ctk.StringVar(value=None)
        data_del_lable1=ctk.CTkLabel(self.frame1, 
                                text='Choose an available doctor', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        data_del_lable1.grid(row=0, column=0, padx=20, pady=10)
        self.cursor.execute('SELECT DISTINCT doctor FROM Appointments WHERE slot_tempo=? AND dispo=1', (slot_sel,))
        docs=self.cursor.fetchall()
        self.combobox_2 = ctk.CTkOptionMenu(self.frame1,
                                        values = [str(do[0]) for do in docs],
                                        #command=self.save_selection
                                        variable=selected_doc
                                        )
        self.combobox_2.grid(row=1, column=0, padx=20, pady=(10, 10))

        ## QUA MANCA METTERE I DOTTORI DISPONIBILI, BISOGNA INVERTIRE CON I TIME SLOT
        #self.scrollable_frame1 = ctk.CTkScrollableFrame(self.frame1, label_text="Select Doctor")
        #self.scrollable_frame1.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        #self.scrollable_frame1.grid_columnconfigure(0, weight=1)
        #self.scrollable_frame_radiobut1 = []
        #self.radio_var1 = ctk.IntVar(value=0)
        # self.label_radio_group = ctk.CTkLabel(self.frame1, text="Available Doctors")
        # if doc_avail_vect is not None:
        #     for j in range(doc_avail):
        #         slot_text_doc=doc_avail_vect[j][0]
        #         radio_button1 = ctk.CTkRadioButton(self.frame1, variable=self.radio_var1, value=j, text=slot_text_doc)
        #         radio_button1.grid(row=j+2, column=0, padx=10, pady=(0, 20))
        #         self.scrollable_frame_radiobut1.append(radio_button1)
        #     doc_sel= self.get_selected_text1()

        self.frame2 = ctk.CTkFrame(scrollable_frame_tot1, fg_color="white")
        self.frame2.grid(row=3, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.frame2.grid_columnconfigure(1, weight=1)

        # === Buttons ===
        confirm_button = ctk.CTkButton(
            self.frame2,
            text="Book appointment",
            height=30,
            width=80,
            font=ctk.CTkFont(size=16),
            command=lambda: self.conferma(slot_sel, selected_doc, user_id)
        )
        confirm_button.grid(row=2, column=0, padx=35, pady=10, sticky="ew")

        print_button = ctk.CTkButton(
            self.frame2,
            text="Print receipt",
            height=30,
            width=80,
            font=ctk.CTkFont(size=16),
            #command=lambda: self.controller.show_page("data") tanto non è chge devo stampare davvero
        )
        print_button.grid(row=3, column=0, padx=35, pady=10, sticky="ew")

        # === Labels ===
        if slot_sel is not None:
            rec1_lable=ctk.CTkLabel(self.frame2, 
                                    text=slot_sel, 
                                    font=('Arial',14),
                                    width=80,
                                    height=20
                                    )
            rec1_lable.grid(row=0, column=0, padx=20, pady=10)
            confirm_button.configure(state="normal")
        else:
            rec1_lable=ctk.CTkLabel(self.frame2, 
                                    text='Please select the visit timeslot', 
                                    font=('Arial',14),
                                    width=80,
                                    height=20
                                    )
            rec1_lable.grid(row=0, column=0, padx=20, pady=10)
            confirm_button.configure(state="disabled")
        
        if selected_doc is not None:
            rec2_lable=ctk.CTkLabel(self.frame2, 
                                    text=selected_doc, 
                                    font=('Arial',14),
                                    width=80,
                                    height=20
                                    )
            rec2_lable.grid(row=1, column=0, padx=20, pady=10)
            print_button.configure(state="normal")
        else:
            rec2_lable=ctk.CTkLabel(self.frame2, 
                                    text='Please select a doctor for the visit', 
                                    font=('Arial',14),
                                    width=80,
                                    height=20
                                    )
            rec2_lable.grid(row=1, column=0, padx=20, pady=10)
            print_button.configure(state="disabled")
        


        #per visualizzare visite già prenotate
        # self.cursor.execute('SELECT n_booked FROM Patients WHERE user_id=?', (user_id,))
        # n_booked_tup= self.cursor.fetchone()
        # n_booked = int(n_booked_tup[0])
        # n_book=len(n_booked_tup)
        # self.cursor.execute('SELECT appointment_id, slot_tempo, doctor FROM Appointments WHERE patient=?', (user_id,))
        # visit_booked=self.cursor.fetchall()

        # === Elenco visite prenotate ===
        # self.scrollable_frame3 = ctk.CTkScrollableFrame(self, label_text="Your booked appointment")
        # self.scrollable_frame3.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)                                            #qua sostituire la composizione di lable a più informazioni
        # self.scrollable_frame3.grid_columnconfigure(0, weight=1)
        # for i in range(n_booked):
        #     visit_x=visit_booked[i][0]
        #     book_lable=ctk.CTkLabel(master=self.scrollable_frame3, 
        #                         text=visit_x,
        #                         font=('Arial',14),
        #                         width=80,
        #                         height=20
        #                         )
        #     book_lable.grid(row=i+1, column=0, padx=20, pady=10, columnspan=3)

        # === Filtro eliminazione visita ===
        # self.scrollable_frame4 = ctk.CTkScrollableFrame(self, label_text="Filter for doctor and time slot", width=500)
        # self.scrollable_frame4.grid(row=1, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        # self.scrollable_frame4.grid_columnconfigure(0, weight=1)
        #del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
        #                        text='Search for visit to forfeit', 
        #                        font=('Arial',14),
        #                        width=300,
        #                        height=30
        #                        )
        #del_lable.grid(row=1, column=0, padx=20, pady=10, columnspan=2)
        # data_del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
        #                         text='Data of undesired visit', 
        #                         font=('Arial',11),
        #                         width=300,
        #                         height=30
        #                         )
        # data_del_lable.grid(row=0, column=0, padx=20, pady=10)
        # doc_del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
        #                         text='Doctor of undesired visit', 
        #                         font=('Arial',11),
        #                         width=300,
        #                         height=30
        #                         )
        # doc_del_lable.grid(row=0, column=2, padx=20, pady=10)

        # self.cursor.execute('SELECT slot_tempo FROM Appointments WHERE patient=?', (user_id,))
        # hours=self.cursor.fetchall()
        # self.combobox_1 = ctk.CTkComboBox(master=self.scrollable_frame4,
        #                                 values = [str(hour[0]) for hour in hours])
        # self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        # self.combobox_1.set("")
        # self.cursor.execute('SELECT doctor FROM Appointments WHERE patient=?', (user_id,))
        # doct=self.cursor.fetchall()
        # self.combobox_2 = ctk.CTkComboBox(master=self.scrollable_frame4,
        #                                 values = [str(doc_str[0]) for doc_str in doct])
        # self.combobox_2.grid(row=1, column=2, padx=20, pady=(10, 10))
        # self.combobox_2.set("")

        # === Elenco visite filtrate tra le possibili da eliminare ===
        # self.scrollable_frame2 = ctk.CTkScrollableFrame(self, label_text="Select visit to forfeit")
        # self.scrollable_frame2.grid(row=2, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        # self.scrollable_frame2.grid_columnconfigure(1, weight=1)
        # self.scrollable_frame_radiobut2 = []
        # self.radio_var2 = ctk.IntVar(value=0)
        # self.label_radio_group2 = ctk.CTkLabel(master=self.scrollable_frame2, text="Available visits")
        # if len(visit_booked)>0:
        #     for i in range(n_book):
        #         booked_round = f"Appointment Code: {visit_booked[i][0]}, Time: {visit_booked[i][1]}, Doctor: {visit_booked[i][2]}"
        #         radio_button1 = ctk.CTkRadioButton(master=self.scrollable_frame2, variable=self.radio_var2, value=i, text=booked_round)
        #         radio_button1.grid(row=i, column=0, padx=10, pady=(0, 20))
        #         self.scrollable_frame_radiobut2.append(radio_button1)
        #     visit_sel= self.get_selected_text2()
        #     code= self.get_codice_appuntamento(visit_sel)
        # else:
        #     self.label_radio_group2 = ctk.CTkLabel(master=self.scrollable_frame2, text="No visit booked")
        #     self.label_radio_group2.grid(row=1, column=0, padx=10, pady=(0, 20), columnspan=3)

        # if len(visit_booked)>0:
        #     eliminate_button = ctk.CTkButton(
        #         master=self.scrollable_frame2,
        #         text="Forfeit selected appointment",
        #         height=30,
        #         width=80,
        #         font=ctk.CTkFont(size=12),
        #         command=lambda: self.eliminate(code)
        #     )
        #     eliminate_button.grid(row=n_book+3, column=5, padx=35, pady=10, sticky="ew")
        #     eliminate_button.configure(state="normal")
        # else:
        #     eliminate_button = ctk.CTkButton(
        #         master=self.scrollable_frame2,
        #         text="Forfeit selected appointment",
        #         height=30,
        #         width=80,
        #         font=ctk.CTkFont(size=12),
        #         command=lambda: self.eliminate(code)
        #     )
        #     eliminate_button.grid(row=n_book+3, column=5, padx=35, pady=10, sticky="ew")
        #     eliminate_button.configure(state="disabled")


        # menu_bar = ctk.CTkFrame(self, fg_color="transparent")
        # menu_bar.grid(row=3, column=5, pady=20)
        # menu_button = ctk.CTkButton(
        #     master=menu_bar,
        #     text="☰ Menu",
        #     width=100,
        #     height=35,
        #     font=ctk.CTkFont(size=14),
        #     command=self.menu_callback
        # )
        # menu_button.grid(row=3, column=5, padx=10, pady=(0, 20))

    #def save_selection(self, value):
    #    self.selected_value = value

    def conferma(self, slot_sel, doc_sel, user, user_id):
        self.cursor.execute('SELECT appointment_id FROM Appointments WHERE slot_tempo=?  AND doctor=?', slot_sel, doc_sel)
        codice=self.cursor.fetchone()
        self.cursor.execute('UPDATE Appointments (patient, dispo) VALUES(?, 0) WHERE appointment_id = ?;', user_id, codice)              #con idea che parto con tabella gia piena con slot ora e dottore, ma dispo=1

    def get_codice_appuntamento(self, visit_sel): #metodo elaborazione stringa
        if visit_sel:
            parts = visit_sel.split(",")
            codice = parts[0].split(":")[1].strip()
            return codice
        return None

    def eliminate(self,code):
        self.cursor.execute("""
                            UPDATE Appointments
                            patient = NULL,
                            dispo=1
                            WHERE appointment_id = ?;
                            """,code)

    def get_selected_text(self):
        selected_index = self.radio_var.get()
        if self.selected_index is not None:
            slot_sel = self.scrollable_frame_radiobut[selected_index].cget("text")
            return slot_sel
        else:
            return None
    
    def get_selected_text1(self):
        if self.selected_index1 is not None:
            selected_index1 = self.radio_var1.get()
            doc_sel = self.scrollable_frame_radiobut1[selected_index1].cget("text")
            return doc_sel
        else:
            return None
        
    def get_selected_text2(self):
        if self.selected_index2 is not None:
            selected_index2 = self.radio_var2.get()
            visit_sel = self.scrollable_frame_radiobut2[selected_index2].cget("text")
            return visit_sel
        else:
            return None

    def menu_callback(self):
        SIDEBAR_WIDTH=250
        self.sidebar_container = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.sidebar_container.grid(row=0, column=0, sticky="ns", rowspan=8)
        self.sidebar_container.grid_rowconfigure(0, weight=1)
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew", rowspan=8)
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Menu",
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Manage Appointment",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                    anchor="w", command=self.home_button_event, width=SIDEBAR_WIDTH)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.frame_2_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Health data record",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_2_button_event, width=SIDEBAR_WIDTH)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")
        self.frame_3_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Emergency communications",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        self.frame_4_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Log out",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_4_button.grid(row=5, column=0, sticky="sew")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Manage Appointment" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Health data record" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "Emergency communications" else "transparent")

        # show selected frame
        if name == "Manage Appointment":
            self.controller.show_internal_page("appointment")
            self.close_sidebar()
        if name == "Health data record":
            self.controller.show_internal_page("data")
            self.close_sidebar()
        if name == "Emergency communications":
            self.controller.show_internal_page("emergency")
            self.close_sidebar()

    def home_button_event(self):
        self.select_frame_by_name("Manage Appointment")

    def frame_2_button_event(self):
        self.select_frame_by_name("Health data record")

    def frame_3_button_event(self):
        self.select_frame_by_name("Emergency communications")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def close_sidebar(self):    #la rimuove dopo che ho scelto una pagina
        self.navigation_frame.grid_remove()  # Nascondi il frame
        self.sidebar_container.grid_remove()
        self.grid_columnconfigure(0, weight=0)
        
class PeriodicQuestionnaire(ctk.CTkFrame):
    def __init__(self, master, controller, patient_id):
        super().__init__(master, fg_color="white")
        self.master = master
        self.patient_id = patient_id
        self.controller = controller
        self.answer_vars = {}
        scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        self.grid_rowconfigure(1, weight=1)  # Allow the scrollable frame to expand

        self.build_ui(scrollable_frame)

    def build_ui(self, parent):
        self.grid_columnconfigure(0, weight=1)  # Allow column to expand

        # Back button 
        back_button = ctk.CTkButton(
            master=parent,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command=lambda: self.controller.show_internal_page("data")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # Check last submission
        recent = last_submission_date(self.patient_id)
        if recent and (datetime.datetime.now().date() - recent.date()).days < 3:
            label = ctk.CTkLabel(
                master=parent,
                text="You already completed the questionnaire for this period.",
                font=("Arial", 16)
            )
            label.grid(row=1, column=0, padx=20, pady=20, sticky="n")
            return

        row = 2
        for i, (field_name, text, *options) in enumerate(get_questions()):
            question_label = ctk.CTkLabel(
                master=parent,
                text=f"{i+1}. {text}",
                anchor="w",
                font=("Arial", 14),
                wraplength=600,  # to handle long questions
                justify="left"
            )
            question_label.grid(row=i*6, column=1, columnspan=2, sticky="w", pady=(10, 2))

            var = ctk.IntVar(value=0)
            self.answer_vars[field_name] = var

            for j, opt in enumerate(options):
                rb = ctk.CTkRadioButton(
                    master=parent,
                    text=opt,
                    variable=var,
                    value=j + 1
                )
                rb.grid(row=i*6 + j + 1, column=1, sticky="w", padx=(20, 0), pady=1)
            row = row + i + j + 1
        
        # Submit Button
        submit_btn = ctk.CTkButton(
            master=parent,
            text="Submit",
            command=self.submit
        )
        submit_btn.grid(row=row, column=1, pady=(10, 500))


    def submit(self):
        if not all(var.get() != 0 for var in self.answer_vars.values()):
            messagebox.showerror("Error", "Answer all questions.")
            return

        answers = {k: v.get() for k, v in self.answer_vars.items()}
        save_submission(self.patient_id, answers)
        messagebox.showinfo("Success", "Questionnaire successfully submitted!")
        self.destroy()
        
class HealthDataPage(ctk.CTkFrame):
    def submit(self):
        if not all(var.get() != 0 for var in self.answer_vars.values()):
            messagebox.showerror("Error", "Answer all questions.")
            return

        answers = {k: v.get() for k, v in self.answer_vars.items()}
        save_submission(self.patient_id, answers)
        messagebox.showinfo("Success", "Questionnaire successfully submitted, come back in 3 days!")
        self.destroy()

    def __init__(self, master, controller, patient_id, return_to="main"):
            super().__init__(master, fg_color="white")
            self.return_to = return_to  
            self.controller = controller
            self.patient_id = patient_id
            self.conn = sqlite3.connect('App/Database/gui_database.db')
            self.cursor = self.conn.cursor()
            self.answer_vars = {}

            scrollable_frame = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
            scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
            scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

            self.patientgui(scrollable_frame, patient_id)

    def patientgui(self, parent, patient_id):
            print(patient_id)

            # === Back Button in Top-Left ===
            back_button = ctk.CTkButton(
                master=parent,
                text="← Back",
                width=60,
                height=30,
                font=ctk.CTkFont(size=14),
                fg_color="#57c2a8",
                hover_color="#034172",
                command=lambda: self.controller.show_internal_page(self.return_to)
            )
            back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

            # === Header Title ===
            ctk.CTkLabel(
                    parent,
                    text="My Data:",
                    font=ctk.CTkFont(size=20, weight="bold")
                ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="e")         

            # === Periodic Questionnaire === 
            quest_button = ctk.CTkButton(
                master=parent,
                text="! Compile Periodic Questionnaire",
                width=60,
                height=30,
                font=ctk.CTkFont(size=14),
                fg_color="#ffbc59",
                hover_color="#e3aa00",
                command=lambda: self.controller.show_questionnaire_page(self.master, self.controller, patient_id)
            )
            quest_button.grid(row=0, column=1, padx=(10, 5), pady=(20, 10), sticky="e")

            # === Fetch patient data ===
            self.cursor.execute("""
                SELECT P.Name, P.Surname, P.Age, P.Gender, P.Diagnosis
                FROM Patients P
                WHERE P.user_id = ?
            """, (patient_id,))
            patient = self.cursor.fetchone()
            name, surname, age, gender, diagnosis = patient

            row = 1
            
            # # Patient info
            # ctk.CTkLabel(
            #     parent,
            #     text=f"🧑‍⚕️ {name} {surname} — Age: {age} — Gender: {gender}",
            #     font=ctk.CTkFont(size=16, weight="bold")
            # ).grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="w")

            # row += 1
            
            # Diagnosis
            diag_text = diagnosis if diagnosis else "No diagnosis available."
            ctk.CTkLabel(
                parent,
                text=f"📋 Diagnosis:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            row += 1

            # Display diagnosis text
            ctk.CTkLabel(
                parent,
                text=f"{diag_text}",
                font=ctk.CTkFont(size=14)
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w")

            row += 1
            # Prescribed therapies
            self.cursor.execute("""
                SELECT D.name, T.dosage, T.duration, T.notes
                FROM Therapy T
                JOIN Drugs D ON T.drug1 = D.drug_id
                WHERE T.patient = ?
            """, (patient_id,))
            therapies = self.cursor.fetchall()

            if therapies:
                ctk.CTkLabel(
                    parent,
                    text="💊 Prescribed Medications:",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).grid(row=row, column=0, padx=10, pady=(10, 5), sticky="w")                
                row += 1

                for med in therapies:
                    info = f"• {med[0]} — {med[1]} for {med[2]} days\n   Note: {med[3]}"
                    ctk.CTkLabel(
                        parent,
                        text=info,
                        font=ctk.CTkFont(size=13)
                    ).grid(row=row, column=0, columnspan=2, padx=15, sticky="w")
                    row += 1
            else:
                pass

            # === Reports ===
            today = "2025-05-29"
            self.cursor.execute("""
                SELECT appointment_id, file_path, created_at
                FROM VisitReport
                WHERE patient = ? 
                AND created_at <= ?
                ORDER BY created_at DESC
            """, (patient_id, today))
            visit_reports = self.cursor.fetchall()

            self.cursor.execute("""
                SELECT snreport_id, file_path, created_at
                FROM SensorsReport
                WHERE patient = ?
                ORDER BY created_at DESC
            """, (patient_id,))
            sensor_reports = self.cursor.fetchall()

            ctk.CTkLabel(
                parent,
                text="📈 Visit Reports:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")

            row += 1

            if visit_reports:
                columns_per_row = 4
                sticky = ["e", "w"]
                for i, (appointment_id, file_path, created_at) in enumerate(sensor_reports):
                    display_text = f"At-home — {created_at.split(' ')[0]}"
                    ctk.CTkButton(
                        parent,
                        text=f"📄 {display_text}",
                        fg_color="#57cc99", 
                        hover_color="#38a3a5",
                        command=lambda path=file_path: show_pdf_in_new_window(path)
                    ).grid(row=row + i // columns_per_row, column=i % columns_per_row, padx=10, pady=5, sticky=sticky)
                row += (len(sensor_reports) - 1) // columns_per_row + 1
            else:
                ctk.CTkLabel(
                    parent,
                    text="No sensor reports available.",
                    font=ctk.CTkFont(size=13, slant="italic")
                ).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                row += 1


            ctk.CTkLabel(
                parent,
                text="📈 Sensors Reports:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")

            row += 1

            if sensor_reports:
                columns_per_row = 4
                sticky = ["e", "w"]
                for i, (report_id, file_path, created_at) in enumerate(sensor_reports):
                    display_text = f"At-home — {created_at.split(' ')[0]}"
                    ctk.CTkButton(
                        parent,
                        text=f"📄 {display_text}",
                        fg_color="#57cc99", 
                        hover_color="#38a3a5",
                        command=lambda path=file_path: show_pdf_in_new_window(path)
                    ).grid(row=row + i // columns_per_row, column=i % columns_per_row, padx=10, pady=5, sticky=sticky)
                row += (len(sensor_reports) - 1) // columns_per_row + 1
            else:
                ctk.CTkLabel(
                    parent,
                    text="No sensor reports available.",
                    font=ctk.CTkFont(size=13, slant="italic")
                ).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                row += 1

            # === Current status === 
            self.cursor.execute("""
                SELECT status
                FROM Sensors 
                WHERE patient = ?
            """, (patient_id,))
            status = self.cursor.fetchone()

            status_text = status[0] if status else "No current status available."
            ctk.CTkLabel(parent, text = "📊 Current Status:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, padx=10, pady=(15, 5), sticky="w")
            row += 1
            ctk.CTkLabel(
                parent,
                text=f"The sensors is: {status_text}",
                font=ctk.CTkFont(size=13)
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(5, 15), sticky="w")
            row += 1

                    
            # === Graphs ===
            image_label = None

            def update_graph_image(choice):
                image_path = {
                    "Last 2 Weeks": "Mario Rossi/Graphs/two_weeks.png",
                    "Last Month": "Mario Rossi/Graphs/last_month.png",
                    "All Time": "Mario Rossi/Graphs/last_month.png",
                }.get(choice, "Mario Rossi/Graphs/two_weeks.png")
                # Should put the fetched name instead of manually, it is to test. The graph should also be shown directly by python
                try:
                    img = ctk.CTkImage(light_image=Image.open(image_path), size=(300, 200))
                    image_label.configure(image=img, text="")
                    image_label.image = img
                except Exception:
                    image_label.configure(text=f"Image not found: {image_path}", image=None)
                    image_label.image = None

            ctk.CTkLabel(
                parent,
                text="📈 PLMI Evolution:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")

            row += 1

            ctk.CTkLabel(
                parent,
                text="Select Timeframe:",
                font=ctk.CTkFont(size=13)
            ).grid(row=row, column=0, padx=10, pady=(10, 0), sticky="w")

            timeframe_dropdown = ctk.CTkOptionMenu(
                parent,
                values=["Last 2 Weeks", "Last Month", "All Time"],
                fg_color="#38a3a5", 
                button_color="#57cc99",
                button_hover_color="#38a3a5",
                command=update_graph_image
            ) 
            timeframe_dropdown.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            timeframe_dropdown.set("Last 2 Weeks")
            row += 1

            image_label = ctk.CTkLabel(parent, text="")
            image_label.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            update_graph_image("Last 2 Weeks")
            row += 1

            # === Questionnaire Averages ===
            show_questionnaire_averages(parent, self, row, patient_id)
            row += 1

class EmergencyPage(ctk.CTkFrame):
    def __init__(self, master,controller, user_id):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.controller = controller
        self.setup_gui(user_id)

    def setup_gui(self, user_id): 
        self.user_id = user_id
        scrollable_frame_tot = ctk.CTkScrollableFrame(self, width=750, height=550, fg_color="white")
        scrollable_frame_tot.grid(pady=20, padx=10)       #, fill="both", expand=True
        scrollable_frame_tot.grid_columnconfigure((0, 1, 2), weight=1)

        # === Back Button in Top-Left ===
        back_button = ctk.CTkButton(
            master=scrollable_frame_tot,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command=lambda: self.controller.show_internal_page("main")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # === Header Title ===
        title_label = ctk.CTkLabel(scrollable_frame_tot, text="🚨 Patient-clinic contacts", font=ctk.CTkFont(size=18))
        title_label.grid(row=0, column=0, pady=(20, 10), columnspan=2)
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        self.frame = ctk.CTkFrame(scrollable_frame_tot, fg_color="white")
        self.frame.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)

        # Main container
        main_frame = ctk.CTkFrame(scrollable_frame_tot, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # ================== LEFT COLUMN: SENSOR REPORT ==================
        left_frame = ctk.CTkFrame(master=main_frame, fg_color="white")
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)

        # Title
        left_title = ctk.CTkLabel(
            master=left_frame,
            text="Report an issue with the sensor",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        left_title.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="w")

        # Fetch sensor names for dropdown
        self.cursor.execute('SELECT Name FROM Sensors WHERE patient=?', (user_id,))
        sensor_names = [row[0] for row in self.cursor.fetchall()]
        default_sensor = sensor_names[0] if sensor_names else "No sensors"

        # Sensor label
        sensor_label = ctk.CTkLabel(master=left_frame, text="Sensor:", font=("Arial", 11))
        sensor_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Sensor dropdown
        self.an2_var = ctk.StringVar(value=default_sensor)
        sensor_menu = ctk.CTkOptionMenu(
            master=left_frame,
            variable=self.an2_var,
            values=sensor_names,
            width=200,
            height=30,
            font=("Arial", 14)
        )
        sensor_menu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # Malfunction date
        date_label = ctk.CTkLabel(master=left_frame, text="Date of the malfunction (YYYY-MM-DD HH:MM):")
        date_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        self.entry_date = ctk.CTkEntry(master=left_frame)
        self.entry_date.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        # Problem description
        desc_label = ctk.CTkLabel(
            master=left_frame,
            text='Describe any problems encountered during the night:',
            font=('Arial', 11),
        )
        desc_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.prob_entry = ctk.CTkTextbox(master=left_frame, width=400, height=80, font=('Arial', 14))
        self.prob_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Submit button
        submit_button = ctk.CTkButton(
            master=left_frame,
            text="Send report",
            height=40,
            width=150,
            font=ctk.CTkFont(size=14),
            command= lambda: self.send_module(user_id)
        )
        submit_button.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="w")

        # ================== RIGHT COLUMN: DOCTOR CONTACT ==================
        right_frame = ctk.CTkFrame(master=main_frame, fg_color="white")
        right_frame.grid(row=0, column=1, padx=(0, 0), sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        # Title
        right_title = ctk.CTkLabel(
            master=right_frame,
            text="Doctor Contact",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        right_title.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="w")


        # Doctor info (dummy data – get this from database in real application)
        doc_info = ctk.CTkLabel(
            master=right_frame,
            text="Dr. Gianna Rossi \nEmail: dr.rossi@quiet.com\nPhone: +123 456 7890",
            font=("Arial", 13),
            justify="left"
        )
        doc_info.grid(row=1, column=0, padx=20, pady=10, sticky="w")

    from datetime import datetime

    def send_module(self, user_id):
        selected_sensor_name = self.an2_var.get()
        malfunction_date = self.entry_date.get()
        problem_description = self.prob_entry.get("1.0", "end").strip()
        created_at = datetime.datetime.now()
        patient_id = user_id 
        try:
            # Get Code_device using the selected sensor name
            self.cursor.execute("SELECT Code_device FROM Sensors WHERE Name=? AND patient=?", (selected_sensor_name, patient_id))
            result = self.cursor.fetchone()

            if result is None:
                self.day_lable.configure(text="Error: Selected sensor not found in database.")
                return

            sensor_id = result[0]

            # Insert into database
            self.cursor.execute("""
                INSERT INTO SensorQuestionnaire (patient, sensor_id, date, created_at, malfunction)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, sensor_id, malfunction_date, created_at, problem_description))
            self.conn.commit()

            # Show success message
            messagebox.showinfo("Submission Successful", "Submitted successfully!\nWe will contact you as soon as possible.\nThank you for your patience.")

        except sqlite3.Error as e:
            print("Database insert failed:", e)
            messagebox.showerror("Submission Failed", "There was an error submitting the form. Please try again.")

    def menu_callback(self):
        SIDEBAR_WIDTH=250
        self.sidebar_container = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.sidebar_container.grid(row=0, column=0, sticky="ns", rowspan=8)
        self.sidebar_container.grid_rowconfigure(0, weight=1)
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew", rowspan=8)
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Menu",
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Manage Appointment",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                    anchor="w", command=self.home_button_event, width=SIDEBAR_WIDTH)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.frame_2_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Health data record",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_2_button_event, width=SIDEBAR_WIDTH)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")
        self.frame_3_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Emergency communications",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        self.frame_4_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Log out",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_4_button.grid(row=5, column=0, sticky="sew")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Manage Appointment" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Health data record" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "Emergency communications" else "transparent")

        # show selected frame
        if name == "Manage Appointment":
            self.controller.show_internal_page("appointment")
            self.close_sidebar()
        if name == "Health data record":
            self.controller.show_internal_page("data")
            self.close_sidebar()
        if name == "Emergency communications":
            self.controller.show_internal_page("emergency")
            self.close_sidebar()

    def home_button_event(self):
        self.select_frame_by_name("Manage Appointment")

    def frame_2_button_event(self):
        self.select_frame_by_name("Health data record")

    def frame_3_button_event(self):
        self.select_frame_by_name("Emergency communications")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def close_sidebar(self):    #la rimuove dopo che ho scelto una pagina
        self.navigation_frame.grid_remove()  # Nascondi il frame
        self.sidebar_container.grid_remove()
        self.grid_columnconfigure(0, weight=0)

        


# == Reference Page == #
class Home_patPage(ctk.CTkFrame):

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.master = master
        self.user_id = user_id

        self.pages = {
            "main": Main(self, self, self.user_id),
            "appointment": AppointmentPage(self, self, self.user_id),
            "data": HealthDataPage(self, self, self.user_id),
            "emergency": EmergencyPage(self, self, self.user_id),
            "visitquest": VisitQuestionnaire(self, self, self.user_id),
            "settings": SettingsPage(self, self, self.user_id),
        }

        print("Pagine create:", list(self.pages.keys()))

        print(self.user_id)
        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def show_questionnaire_page(self, master, controller, patient_id):
        # Hide or destroy the current page if it exists
        current_page = self.pages.get("current")
        if current_page is not None:
            current_page.grid_forget()  # or use current_page.destroy() if you want to fully delete it

        # Create and show the new page
        questionnaire_page = PeriodicQuestionnaire(master, controller, patient_id)
        questionnaire_page.grid(row=0, column=0, sticky="nsew")
        questionnaire_page.tkraise()

        # Update pages tracking
        self.pages["current"] = questionnaire_page

