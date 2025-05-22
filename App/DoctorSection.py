import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime
import os
from tkinter import messagebox

class VisitDetails(ctk.CTkFrame):

    def __init__(self, master, controller, user_id, appointment_id):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.controller = controller
        self.appointment_id = appointment_id
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        

        self.cursor.execute("""
        SELECT visit_type
        FROM Appointments A
        WHERE A.appointment_id = ?
        """, (self.appointment_id,))

        appointment_type = self.cursor.fetchone()

        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.visitgui(scrollable_frame)

    def visitgui(self, parent):

        # Get patient and visit info
        self.cursor.execute("""
        SELECT P.user_id, P.Name, P.Surname, P.Age, P.Gender, P.Diagnosis, P.Theraphy, A.visit_type
        FROM Appointments A
        JOIN Patients P ON A.patient = P.user_id
        WHERE A.appointment_id = ?
        """, (self.appointment_id,))

        patient_data = self.cursor.fetchone()
        if not patient_data:
            return

        patient_id, name, surname, age, gender, diagnosis, therapy, visit_type = patient_data

        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(parent, text="🩺 Visit Details", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))

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

        # ==== Patient Info ====
        ctk.CTkLabel(parent, text=f"Name: {name} {surname}", font=ctk.CTkFont(size=12)).grid(row=1, column=1, sticky="w", pady=5)
        ctk.CTkLabel(parent, text=f"Age: {age}", font=ctk.CTkFont(size=12)).grid(row=2, column=1, sticky="w", pady=5)
        ctk.CTkLabel(parent, text=f"Gender: {gender}", font=ctk.CTkFont(size=12)).grid(row=3, column=1, sticky="w", pady=5)

        # ==== Questionnaire or Sensor Report ====
        if visit_type == 1:  # Assuming '1' = first visit
            quest_button = ctk.CTkButton(parent, text="Open First Visit Questionnaire PDF", command=self.open_questionnaire_pdf)
            quest_button.grid(row=4, column=1, pady=10)
        else:
            report_button = ctk.CTkButton(parent, text="Open Last Sensor Report", command=self.open_sensor_report_pdf)
            report_button.grid(row=4, column=1, pady=10)

        # ==== Doctor Notes Entry ====
        ctk.CTkLabel(parent, text="Doctor Notes:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=1, pady=(15, 5))
        self.notes_entry = ctk.CTkTextbox(parent, height=100, width=300)
        self.notes_entry.grid(row=6, column=1, pady=5)

        # ==== Current Diagnosis ====
        ctk.CTkLabel(parent, text=f"Diagnosis:", font=ctk.CTkFont(size=16)).grid(row=7, column=1, pady=5)
        self.diagnosis_entry = ctk.CTkEntry(parent, width=300)
        self.diagnosis_entry.insert(0, diagnosis if diagnosis else "")
        self.diagnosis_entry.grid(row=8, column=1, pady=5)

        # ==== Current Therapy (Editable) ====
        ctk.CTkLabel(parent, text=f"Current Therapy:", font=ctk.CTkFont(size=16)).grid(row=9, column=1, pady=5)
        self.therapy_entry = ctk.CTkTextbox(parent, height=60, width=300)
        self.therapy_entry.insert("1.0", therapy if therapy else "")
        self.therapy_entry.grid(row=10, column=1, pady=5)

        # ==== Active Therapies from Therapy Table ====
        self.cursor.execute("""
            SELECT D.name, T.dosage, T.duration, T.notes
            FROM Therapy T
            JOIN Drugs D ON T.drug1 = D.drug_id
            WHERE T.patient = ?
        """, (patient_id,))
        therapy_list = self.cursor.fetchall()

        if therapy_list:
            ctk.CTkLabel(parent, text="Prescribed Drugs:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=11, column=1, pady=(10, 5))
            for idx, (drug, dosage, duration, note) in enumerate(therapy_list):
                info = f"{drug}: {dosage}, {duration} days\nNote: {note}"
                ctk.CTkLabel(parent, text=info, font=ctk.CTkFont(size=14)).grid(row=12+idx, column=1, sticky="w", pady=2)

        # ==== Button to Issue Prescription ====
        prescribe_button = ctk.CTkButton(
            parent, text="➕ Issue Prescription", fg_color="#1e81b0", hover_color="#145374"
        )
        prescribe_button.grid(row=100, column=1, pady=20)

    def open_questionnaire_pdf(self):
        os.system("open files/first_visit_questionnaire.pdf")  # Adjust path as needed

    def open_sensor_report_pdf(self):
        os.system("open files/last_sensor_report.pdf")  # Adjust path as needed

class Main(ctk.CTkFrame):   
    def toggle_manage_mode(self):
        self.manage_mode = not self.manage_mode
        self.manage_btn.configure(
            text="✅ Exit Manage Mode" if self.manage_mode else "🛠 Manage Appointments"
        )
        self.show_appointments("all", user_id=self.controller.user_id)

    def __init__(self, master, controller, user_id=None):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        self.manage_mode = False

        # Scrollable frame for appointments
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.Appointment_doc_gui(scrollable_frame, user_id)

    def Appointment_doc_gui(self, parent, user_id):
        self.appointments_container = parent
        parent.grid_columnconfigure((0, 1, 2), weight=1)

        # === Header & Profile ===
        ctk.CTkLabel(parent, text="Welcome, Doctor!", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=1, columnspan=2, pady=(20, 5), sticky="w")
        
        try:
            profile_img = ctk.CTkImage(light_image=Image.open("App/doctorprofile.png"), size=(50, 50))
            profile_pic = ctk.CTkLabel(parent, image=profile_img, text="")
            profile_pic.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        except:
            pass

        ctk.CTkLabel(parent, text="My Appointments:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, pady=(10, 10))

        # === Filter Buttons ===
        button_config = {
            "height": 45,
            "corner_radius": 3,
            "font": ctk.CTkFont(size=15),
            "hover_color" :"#38a3a5",
            "fg_color":"#57cc99",
            "text_color": "white"
        }

        sticky = ["e", "", "w"]
        filters = [("Today", "today"), ("Tomorrow", "tomorrow"), ("All", "all")]
        for i, (text, key) in enumerate(filters):
            ctk.CTkButton(
                master=parent,
                text=text,
                command=lambda k=key: self.show_appointments(k, user_id),
                **button_config
            ).grid(row=3, column=i, padx=5, pady=10, sticky = sticky[i])

        self.manage_btn = ctk.CTkButton(
            self.appointments_container,
            text="🛠 Manage Appointments",
            width=180,
            corner_radius=10,
            fg_color="#57cc99",
            hover_color="#38a3a5",
            text_color="white",
            font=ctk.CTkFont(size=14),
            command=self.toggle_manage_mode
        )
        self.manage_btn.grid(row=1000, column=0, columnspan=3, pady=(30, 10))

        self.cursor.execute("""
            SELECT user_id, Name || ' ' || Surname AS full_name
            FROM Patients
            WHERE assigned_doctor = ?
        """, (user_id,))

        patients = self.cursor.fetchall()  
        self.patient_id_map = {full_name: user_id for user_id, full_name in patients}
        patient_names = list(self.patient_id_map.keys())  # Names shown in dropdown

        ctk.CTkLabel(parent, text="My Patients:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1001, column=0, pady=(10,500))

        self.optionmenu = ctk.CTkOptionMenu(parent,
                                            text_color = "#38a3a5",
                                            corner_radius = 3, 
                                            fg_color= "#38a3a5",
                                            button_color ="#38a3a5",
                                            button_hover_color="#57cc99",
                                            values=patient_names, 
                                            command=self.optionmenu_callback)
        self.optionmenu.grid(row=1001, column=1, padx=5, pady=(10,500), sticky="ew")

    
    def optionmenu_callback(self, selected_name):
        patient_id = self.patient_id_map[selected_name]
        #self.controller.show_internal_page("patient", patient_id)

    def show_appointments(self, time_slot, user_id):
        for widget in self.appointments_container.winfo_children():
            grid_info = widget.grid_info()
            if 4 <= int(grid_info.get("row", 0)) < 500:
                widget.destroy()

        params = []
        where_clauses = []

        if time_slot in ["today", "tomorrow"]:
            today_str = "2025-05-29" if time_slot == "today" else "2025-05-30"
            where_clauses.append("date(A.slot_tempo) = ?")
            params.append(today_str)
            no_appointments_text = f"No {time_slot} appointments 💤"
        else:
            no_appointments_text = "No appointments available 💤"

        where_clauses.append("A.doctor = ?")
        params.append(user_id)

        if where_clauses:
            time_condition = "WHERE " + " AND ".join(where_clauses)
        else:
            time_condition = ""

        query = f"""
            SELECT 
                A.slot_tempo, 
                A.visit_type,
                P.Name,
                P.Surname,
                A.appointment_id
            FROM Appointments A
            JOIN Patients P ON A.patient = P.user_id
            {time_condition}
            ORDER BY A.slot_tempo ASC
        """

        self.cursor.execute(query, tuple(params))
        appointments = self.cursor.fetchall()

        if not appointments:
            ctk.CTkLabel(self.appointments_container, text=no_appointments_text, text_color="#999").grid(row=3, column=0, columnspan=3, pady=20)
            return

        row = 4
        for appointment in appointments:
            time_str = appointment[0].split(' ')[1][:5]
            visit_type = appointment[1]
            self.cursor.execute("SELECT Visit FROM Visits WHERE visit_code = ?", (visit_type,))
            visit_name = self.cursor.fetchone()
            visit_name_str = visit_name[0] if visit_name else "Unknown"
            patient_name = f"{appointment[2]} {appointment[3]}"
            appointment_id = appointment[4]

            if self.manage_mode:
                apt_label = ctk.CTkLabel(
                    self.appointments_container,
                    text=f"{time_str} 🕒 | {patient_name} | {visit_name_str}",
                    font=ctk.CTkFont(size=14),
                    text_color="#222"
                )
                apt_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=5, padx=(5, 0))

                del_button = ctk.CTkButton(
                    self.appointments_container,
                    text="❌",
                    width=30,
                    height=30,
                    font=ctk.CTkFont(size=14),
                    fg_color="#ff6b6b",
                    hover_color="#ff4d4d",
                    text_color="white",
                    command=lambda aid=appointment_id: self.delete_appointment(aid)
                )
                del_button.grid(row=row, column=2, sticky="e", padx=(0, 5))
            else:
                apt_button = ctk.CTkButton(
                    self.appointments_container,
                    text=f"{time_str} 🕒 | {patient_name} | {visit_name_str}",
                    width=320,
                    height=40,
                    font=ctk.CTkFont(size=14),
                    corner_radius=10,
                    fg_color= "#FFE5B4",
                    hover_color= "#FFD6A5",
                    text_color="#222",
                    command=lambda vt=appointment_id: self.controller.show_visit_page(vt, user_id)
                )
                apt_button.grid(row=row, column=0, columnspan=3, pady=5)

            row += 1


    def manage_appointment(self, appointment_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this appointment?"):
            self.cursor.execute("DELETE FROM Appointments WHERE appointment_id = ?", (appointment_id,))
            self.conn.commit()
            self.show_appointments("all", user_id=self.controller.user_id)

# === Main Page Controller ===
class Home_docPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.master = master
        self.controller = controller
        self.user_id = user_id

        self.pages = {}
        self.grid_columnconfigure(0, weight=1)

        self.pages["main"] = Main(self, self, self.user_id)
        #self.pages["visit_details"] = VisitDetails(self, self, self.user_id)

        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def show_visit_page(self, sensor_id, user_id):
        visit_details_page = VisitDetails(self, self, user_id, sensor_id)
        self.pages["visit_details"] = visit_details_page
        visit_details_page.grid(row=0, column=0, sticky="nsew")
        visit_details_page.tkraise()