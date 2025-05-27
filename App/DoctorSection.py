import customtkinter as ctk
from tkinter import messagebox

import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk

import sqlite3
import datetime
from datetime import datetime
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def show_pdf_in_new_window(pdf_path):
    doc = fitz.open(pdf_path)

    win = tk.Toplevel()
    win.title("PDF Viewer")
    win.geometry("1000x800")
    win.grab_set()

    canvas = tk.Canvas(win, bg="white")
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg="white")
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update scroll region on frame config
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Store image refs
    image_refs = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=100)  # 100 DPI = lighter and scrollable
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo = ImageTk.PhotoImage(img)

        label = tk.Label(scrollable_frame, image=photo, bg="white")
        label.image = photo
        image_refs.append(photo)
        label.pack(pady=10)

    # ==============================
    # Scroll binding (cross-platform)
    def _on_mousewheel(event):
        # Windows and Linux
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mac_scroll(event):
        # macOS needs delta directly
        canvas.yview_scroll(-1 * event.delta, "units")

    def bind_scroll_events():
        system = win.tk.call('tk', 'windowingsystem')
        if system == 'aqua':
            canvas.bind_all("<MouseWheel>", _on_mac_scroll)
        else:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def unbind_scroll_events():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    scrollable_frame.bind("<Enter>", lambda e: bind_scroll_events())
    scrollable_frame.bind("<Leave>", lambda e: unbind_scroll_events())

    def on_close():
        unbind_scroll_events()
        win.grab_release()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)
    doc.close()

def show_questionnaire_averages(parent, controller, row, patient_id):
        ctk.CTkLabel(
            parent,
            text="📝 Questionnaire Averages:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")
        row += 1

        # --- Timeframe Selection ---
        ctk.CTkLabel(
            parent,
            text="Select Timeframe:",
            font=ctk.CTkFont(size=13)
        ).grid(row=row, column=0, padx=10, pady=(10, 0), sticky="w")
        row += 1

        # Container for dynamic labels
        questionnaire_labels = []

        def refresh_questionnaire_averages(timeframe, row):
            # Clear old labels
            for lbl in questionnaire_labels:
                lbl.destroy()
            questionnaire_labels.clear()

            # Get date filter based on timeframe
            from datetime import datetime, timedelta

            today = datetime.today()
            if timeframe == "Last 2 Weeks":
                #since_date = today - timedelta(weeks=2)
                base_date = datetime.strptime("2025-05-29", "%Y-%m-%d")
                since_date = base_date - timedelta(weeks=2)
            elif timeframe == "Last Month":
                base_date = datetime.strptime("2025-05-30", "%Y-%m-%d")
                since_date = base_date - timedelta(weeks=2)
            else:
                since_date = None  # All time

            # Fetch questions
            controller.cursor.execute("""
                SELECT field_name, question_text, option_1, option_2, option_3, option_4, option_5 
                FROM QuestionDefinitions
            """)
            questions = controller.cursor.fetchall()

            for q in questions:
                field, text, *options = q
                if since_date:
                    controller.cursor.execute(f"""
                        SELECT AVG({field})
                        FROM PeriodicQuestionnaire
                        WHERE patient_id = ? AND date >= ?
                    """, (patient_id, since_date.strftime("%Y-%m-%d")))
                else:
                    controller.cursor.execute(f"""
                        SELECT AVG({field})
                        FROM PeriodicQuestionnaire
                        WHERE patient_id = ?
                    """, (patient_id,))
                avg = controller.cursor.fetchone()[0]

                if avg:
                    mean_value = round(avg)
                    meaning = options[mean_value - 1] if 1 <= mean_value <= 5 else "Unknown"
                    msg = f"{text} → Mean: {mean_value} ({meaning})"
                else:
                    msg = f"{text} → No data"

                lbl = ctk.CTkLabel(parent, text=msg, font=ctk.CTkFont(size=13))
                lbl.grid(row=row, column=0, columnspan=2, padx=15, pady=2, sticky="w")
                questionnaire_labels.append(lbl)
                row += 1
        # --- Dropdown for timeframe ---
        timeframe_dropdown = ctk.CTkOptionMenu(
            parent,
            values=["Last 2 Weeks", "Last Month", "All Time"],
            fg_color="#38a3a5", 
            button_color="#57cc99",
            button_hover_color="#38a3a5",
            command=lambda value: refresh_questionnaire_averages(value, row)
        )
        timeframe_dropdown.grid(row=row-1, column=0, padx=10, pady=5, sticky="e")
        timeframe_dropdown.set("Last 2 Weeks")
        refresh_questionnaire_averages("Last 2 Weeks", row)  # Initial load
        row += 1

class openQuestionaire(ctk.CTkFrame):
    def __init__(self, master, controller, app_id, patient_id, visit_type="first_visit"):
        super().__init__(master, fg_color="white")
        self.patient_id = patient_id
        self.controller = controller
        self.appointment_id = app_id
        self.visit_type = visit_type
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.questionnaire_gui(scrollable_frame)

    def questionnaire_gui(self, parent):
        # Add your questionnaire GUI code here
        title_label = ctk.CTkLabel(parent, text="📝 Questionnaire", font=ctk.CTkFont(size=22, weight="bold")
                                   )
        title_label.grid(row=0, column=1, pady=(20, 10))
        
        # Back Button
        back_button = ctk.CTkButton(
            master=parent,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command=lambda: self.controller.show_visit_page(self.patient_id, self.appointment_id)
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # Visit Questionnaire
        if self.visit_type == "first_visit":
            self.display_questionnaire_answers(parent)

        # Periodic Questionnaire
        if self.visit_type == "periodic":
            show_questionnaire_averages(parent, self, 1, self.patient_id)
    
    def display_questionnaire_answers(self, parent):
        # Fetch answers from DB
        self.cursor.execute("SELECT * FROM VisitQuestionnaire WHERE appointment_id=?", (self.appointment_id,))
        result = self.cursor.fetchone()

        if not result:
            ctk.CTkLabel(parent, text="No questionnaire found.", text_color="red").grid(row=0, column=0, padx=10, pady=10)
            return

        (
            vquest_id, _, pathologies, medication, physicalactivity, sleephours,
            sleepquality, diet, tobacco, alcohol, stress, notes, created_at
        ) = result

        current_row = 1  # Start after any headers or other content

        def add_info_row(container, row, label, value):
            ctk.CTkLabel(container, text=f"{label}:", anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", padx=(10, 5), pady=2)
            ctk.CTkLabel(container, text=value if value else "N/A", anchor="w", wraplength=250).grid(row=row, column=1, sticky="w", padx=5, pady=2)

        def create_section(title):
            nonlocal current_row
            section_frame = ctk.CTkFrame(parent, fg_color="#f0f0f0", corner_radius=10)
            section_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
            ctk.CTkLabel(section_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 10))
            section_frame.grid_columnconfigure((0, 1), weight=1)
            current_row += 1
            return section_frame

        # Section 1: Medical Info
        medical_section = create_section("🩺 Medical Info")
        add_info_row(medical_section, 1, "Pathologies", pathologies)
        add_info_row(medical_section, 2, "Medication", medication)

        # Section 2: Lifestyle
        lifestyle_section = create_section("🏃 Lifestyle & Habits")
        add_info_row(lifestyle_section, 1, "Physical Activity", physicalactivity)
        add_info_row(lifestyle_section, 2, "Tobacco", tobacco)
        add_info_row(lifestyle_section, 3, "Alcohol", alcohol)
        add_info_row(lifestyle_section, 4, "Diet", diet)
        add_info_row(lifestyle_section, 5, "Stress", stress)

        # Section 3: Sleep
        sleep_section = create_section("😴 Sleep")
        add_info_row(sleep_section, 1, "Sleep Hours", sleephours)
        add_info_row(sleep_section, 2, "Sleep Quality", sleepquality)

        # Section 4: Notes
        notes_section = create_section("🗒️ Notes")
        notes_label = ctk.CTkLabel(notes_section, text="Notes:", anchor="w", font=ctk.CTkFont(weight="bold"))
        notes_label.grid(row=1, column=0, sticky="nw", padx=(10, 5), pady=5)

        notes_box = ctk.CTkTextbox(notes_section, height=80, width=250)
        notes_box.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        notes_box.insert("0.0", notes if notes else "No notes provided.")
        notes_box.configure(state="disabled")

        # Timestamp
        ctk.CTkLabel(parent, text=f"🕓 Submitted on: {created_at}", text_color="gray").grid(
            row=current_row + 1, column=0, columnspan=2, pady=(10, 0), padx=10, sticky="w"
        )

class VisitDetails(ctk.CTkFrame):

    def __init__(self, master, controller, user_id, appointment_id, return_to="main"):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.return_to = return_to  
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
            command=lambda: self.controller.show_internal_page(self.return_to)
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # ==== Patient Info ====
        ctk.CTkLabel(parent, text=f"Name: {name} {surname}, Age: {age}, Gender: {gender}", font=ctk.CTkFont(size=12)).grid(row=1, column=1, sticky="ew", pady=5)
       
        row = 2
        # ==== Questionnaire or Sensor Report ====
        if visit_type == 1:  # Assuming '1' = first visit
            quest_button = ctk.CTkButton(parent, text="Open First Visit Questionnaire PDF", command= lambda: self.controller.show_open_questionnaire(self.appointment_id, patient_id, visit_type="first_visit"))
            quest_button.grid(row=2, column=1, pady=10)
            row = 3

        else:
            # -- Sensor Reports --
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


            ctk.CTkLabel(parent, text="📈 Visit Reports:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=row, column=0, padx=10, pady=(15, 5), sticky="w")
            row += 1
            
            sticky = ["w", "nw"]
            if visit_reports:
                for report_id, file_path, created_at in visit_reports:
                    display_text = f"Past Visit — {created_at.split(' ')[0]}"
                    # File path should have patient name added
                    ctk.CTkButton(parent, 
                                text= f"📄 {display_text}",
                                command=lambda path=file_path: show_pdf_in_new_window(path)
                                ).grid(row=row, column=0, padx=20, pady=5, sticky= sticky)
                    row += 1
            else:
                ctk.CTkLabel(parent, text="No past visit reports available.", font=ctk.CTkFont(size=13, slant="italic")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                row += 1

            ctk.CTkLabel(parent, text="📈 Sensor Reports:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=row-1, column=0, padx=10, pady=(15, 5), sticky="sw")

            if sensor_reports:
                for report_id, file_path, created_at in sensor_reports:
                    display_text = f"Sensor Reports: — {created_at.split(' ')[0]}"
                    # File path should have patient name added

                    ctk.CTkButton(parent, 
                                text= f"📄 {display_text}",
                                command=lambda path=file_path: show_pdf_in_new_window(path)
                                ).grid(row=row, column=0, padx=20, pady=5, sticky="w")
                    row += 1
            else:
                ctk.CTkLabel(parent, text="No past sensors reports available.", font=ctk.CTkFont(size=13, slant="italic")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                row += 1


            report_button = ctk.CTkButton(parent, text="Open Periodic Questionnaires", 
                                          command= lambda: self.controller.show_open_questionnaire(self.appointment_id, patient_id, visit_type="periodic"))
            report_button.grid(row=2, column = 1, pady=10)
            row = 3


        # ==== Doctor Notes Entry ====
        ctk.CTkLabel(parent, text="Doctor Notes:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row, column=1, pady=(15, 5))
        self.notes_entry = ctk.CTkTextbox(parent, fg_color= "#dee2e6", height=100, width=300)
        self.notes_entry.grid(row=row+1, column=1, pady=5)

        # ==== Current Diagnosis ====
        ctk.CTkLabel(parent, text=f"Diagnosis:", font=ctk.CTkFont(size=16)).grid(row=row+2, column=1, pady=5)
        self.diagnosis_entry = ctk.CTkEntry(parent, width=300)
        self.diagnosis_entry.insert(0, diagnosis if diagnosis else "")
        self.diagnosis_entry.grid(row=row+3, column=1, pady=5)

        # ==== Active Therapies from Therapy Table ====
        self.cursor.execute("""
            SELECT D.name, T.dosage, T.duration, T.notes
            FROM Therapy T
            JOIN Drugs D ON T.drug1 = D.drug_id
            WHERE T.patient = ?
        """, (patient_id,))
        therapy_list = self.cursor.fetchall()

        if therapy_list:
            ctk.CTkLabel(parent, text="Prescribed Drugs:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row+4, column=1, pady=(10, 5))
            for idx, (drug, dosage, duration, note) in enumerate(therapy_list):
                info = f"{drug}: {dosage}, {duration} days\nNote: {note}"
                ctk.CTkLabel(parent, text=info, font=ctk.CTkFont(size=14)).grid(row=row+5+idx, column=1, sticky="w", pady=2) 
            row = row + len(therapy_list)

        # ==== Add Therapy (Editable) ====
        # ctk.CTkLabel(parent, text="Add New Therapy:", font=ctk.CTkFont(size=16)).grid(row=row+6, column=1, pady=5)
        # self.therapy_entry = ctk.CTkTextbox(parent, height=60, width=300)
        # self.therapy_entry.insert("1.0", therapy if therapy else "")
        # self.therapy_entry.grid(row=row+7, column=1, pady=5)

        # ==== Button to Issue Prescription ====
        prescribe_button = ctk.CTkButton(
            parent, text="➕ Issue Prescription", fg_color="#1e81b0", hover_color="#145374"
            , command=lambda: self.controller.show_prescription_page(1, self.user_id, patient_id=patient_id, app_id = self.appointment_id)
            
        )
        prescribe_button.grid(row=100, column=1, pady=10)

        # ==== Generate Report ====
        prescribe_button = ctk.CTkButton(
            parent, text="✔️​ Generate Report", fg_color="#145374", hover_color="#1e81b0",
            command = lambda: self.generate_pdf_report(self, patient_id)
        )
        prescribe_button.grid(row=101, column=1, pady=(10,500))

    def generate_pdf_report(parent, patient_id):
        # Fetch patient name
        parent.cursor.execute("SELECT Name, Surname FROM Patients WHERE user_id = ?", (patient_id,))
        patient_info = parent.cursor.fetchone()
        if not patient_info:
            print("Patient not found")
            return

        name, surname = patient_info
        full_name = f"{name} {surname}"
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Build the path
        dir_path = os.path.join(full_name, "Reports", "VisitReports")
        os.makedirs(dir_path, exist_ok=True)
        pdf_path = os.path.join(dir_path, f"{date_str}.pdf")

        # Generate PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Visit Report for {full_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 30

        # Loop over widgets in column 1 of `parent`
        for child in parent.winfo_children():
            grid_info = child.grid_info()
            if grid_info.get("column") == 1:
                try:
                    text = child.cget("text")
                    if text:
                        for line in text.split("\n"):
                            c.drawString(50, y, line)
                            y -= 20
                            if y < 50:
                                c.showPage()
                                y = height - 50
                except Exception:
                    continue

        c.save()
        print(f"PDF saved to {pdf_path}")

class IssuePrescription(ctk.CTkFrame):
    def __init__(self, master, controller, mode, user_id, patient_id, app_id = None):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.appointment_id = app_id
        self.patient_id = patient_id
        self.mode = mode  # 1 for visit, 2 for patient page
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.prescription_gui(scrollable_frame)

    def prescription_gui(self, parent):
        # Add your prescription GUI code here
        title_label = ctk.CTkLabel(parent, text="💊 Issue Prescription", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))


        # Back Button

        if self.mode == 1:
            back_command = lambda: self.controller.show_patient_page(self.user_id, self.patient_id)
        else:
            back_command = lambda: self.controller.show_visit_page(self.user_id, self.appointment_id)


        back_button = ctk.CTkButton(
            master=parent,
            text="← Back",
            width=60,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="#57c2a8",
            hover_color="#034172",
            command = back_command
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # Prescription Form
        ctk.CTkLabel(parent, text="Patient ID: " + str(self.patient_id), font=ctk.CTkFont(size=14)).grid(row=1, column=0, columnspan=2)

        ctk.CTkLabel(parent, text="Drug Name:", font=ctk.CTkFont(size=14)).grid(row=2, column=0)
        self.drug_name_entry = ctk.CTkEntry(parent)
        self.drug_name_entry.grid(row=2, column=1)

        ctk.CTkLabel(parent, text="Dosage:", font=ctk.CTkFont(size=14)).grid(row=3, column=0)
        self.dosage_entry = ctk.CTkEntry(parent)
        self.dosage_entry.grid(row=3, column=1)

        ctk.CTkLabel(parent, text="Duration (days):", font=ctk.CTkFont(size=14)).grid(row=4, column=0)
        self.duration_entry = ctk.CTkEntry(parent)
        self.duration_entry.grid(row=4, column=1)

        ctk.CTkLabel(parent, text="Notes:", font=ctk.CTkFont(size=14)).grid(row=5, column=0)
        self.notes_entry = ctk.CTkTextbox(parent, height=60, width=300)
        self.notes_entry.grid(row=5, column=1, pady=5)

        # Issue Prescription Button
        issue_button = ctk.CTkButton(
            parent, text="➕ Issue Prescription", fg_color="#1e81b0", hover_color="#145374",
            command=self.issue_prescription)
        issue_button.grid(row=6, column=1, pady=(10, 20))

    def issue_prescription(self):
        drug_name = self.drug_name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        duration = self.duration_entry.get().strip()
        notes = self.notes_entry.get("1.0", "end-1c").strip()

        if not drug_name or not dosage or not duration:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number.")
            return
        
        self.cursor.execute("SELECT name || ' ' || surname FROM Patients WHERE user_id = ?", (self.patient_id,))
        patient_fullname = self.cursor.fetchone()[0]

        path = f"{patient_fullname}/Reports/Prescriptions/{self.patient_id}_prescription.pdf"
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        presc_type = "Drug Prescription"

        # Insert into Prescription table
        self.cursor.execute("""
            INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.appointment_id, self.patient_id, self.user_id, path, data, presc_type))

        # Get the ID of the newly inserted prescription
        prescription_id = self.cursor.lastrowid

        # Insert into PrescriptionDrugs table
        self.cursor.execute("""
            INSERT INTO PrescriptionDrugs (prescription_id, drug_name, dosage, duration, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (prescription_id, drug_name, dosage, duration, notes))
        # Should insert into Drugs table if not exists

        # Insert into Therapy table
        self.cursor.execute("""
            INSERT INTO Therapy (patient, drug1, dosage, duration, notes)
            VALUES (?, (SELECT drug_id FROM Drugs WHERE name = ?), ?, ?, ?)
        """, (self.patient_id, drug_name, dosage, duration, notes))
        
        self.conn.commit()
        messagebox.showinfo("Success", "Prescription issued successfully!")
        self.controller.show_patient_page(self.user_id, self.patient_id)

class PatientPage(ctk.CTkFrame): 
    def __init__(self, master, controller, patient_id, user_id, return_to="main"):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.return_to = return_to  
        self.controller = controller
        self.patient_id = patient_id
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
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

        # === Fetch patient data ===
        self.cursor.execute("""
            SELECT P.Name, P.Surname, P.Age, P.Gender, P.Diagnosis
            FROM Patients P
            WHERE P.user_id = ?
        """, (patient_id,))
        patient = self.cursor.fetchone()
        name, surname, age, gender, diagnosis = patient

        row = 1
        # Patient info
        ctk.CTkLabel(
            parent,
            text=f"🧑‍⚕️ {name} {surname} — Age: {age} — Gender: {gender}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        row += 1
        # Diagnosis
        diag_text = diagnosis if diagnosis else "No diagnosis available."
        ctk.CTkLabel(
            parent,
            text=f"📋 Diagnosis: {diag_text}",
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

            # Prescription button to the right
            prescribe_button = ctk.CTkButton(
                parent,
                text="➕ Issue Prescription",
                fg_color="#1e81b0",
                hover_color="#145374",
                command=lambda: self.controller.show_prescription_page(2, self.user_id, patient_id=patient_id, app_id=None)
            )
            prescribe_button.grid(row=row, column=1, padx=10, pady=(10, 5), sticky="e")

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
            # Still show the prescribe button if no therapies
            prescribe_button = ctk.CTkButton(
                parent,
                text="➕ Issue Prescription",
                fg_color="#1e81b0",
                hover_color="#145374",
                command=lambda: self.controller.show_prescription_page(self.user_id, patient_id=patient_id, app_id=None)
            )
            prescribe_button.grid(row=row, column=0, padx=10, pady=(10, 5), sticky="w")
            row += 1

        # === Sensor Reports ===
        self.cursor.execute("""
            SELECT snreport_id, file_path, created_at
            FROM SensorsReport
            WHERE patient = ?
            ORDER BY created_at DESC
        """, (patient_id,))
        sensor_reports = self.cursor.fetchall()

        ctk.CTkLabel(
            parent,
            text="📈 Sensor Reports:",
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

        # === Graphs ===
        image_label = None

        def update_graph_image(choice):
            image_path = {
                "Last 2 Weeks": "Mario Rossi/Graphs/two_weeks.png",
                "Last Month": "Mario Rossi/Graphs/last_month.png",
                "All Time": "Mario Rossi/Graphs/last_month.png",
            }.get(choice, "Mario Rossi/Graphs/two_weeks.png")

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

class Main(ctk.CTkFrame):   
    def toggle_manage_mode(self):
        self.manage_mode = not self.manage_mode
        self.manage_btn.configure(
            text="✅ Exit Manage Mode" if self.manage_mode else "🛠 Manage Appointments"
        )
        self.show_appointments("all", user_id=self.controller.user_id)

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        self.manage_mode = False
        self.user_id = user_id

        # Scrollable frame for appointments
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.Appointment_doc_gui(scrollable_frame, user_id)

    def Appointment_doc_gui(self, parent, user_id):
        self.user_id = user_id
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

        ctk.CTkLabel(parent, text="📅 My Appointments:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, pady=(10, 10))

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

        ctk.CTkLabel(parent, text="🗂️ My Patients:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1001, column=0, pady=(10,500), sticky = "w")

        self.optionmenu = ctk.CTkOptionMenu(parent,
                                            text_color = "#38a3a5",
                                            corner_radius = 3, 
                                            fg_color= "#38a3a5",
                                            button_color ="#38a3a5",
                                            button_hover_color="#57cc99",
                                            values=patient_names, 
                                            command=lambda selected_name: self.optionmenu_callback(selected_name, user_id))
        self.optionmenu.grid(row=1001, column=1, padx=5, pady=(10,500), sticky="ew")

    
    def optionmenu_callback(self, selected_name, user_id):
        patient_id = self.patient_id_map[selected_name]
        self.controller.show_patient_page(user_id, patient_id)

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
                    corner_radius=15,
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
                    command=lambda vt=appointment_id: self.controller.show_visit_page(user_id, vt)
                )
                apt_button.grid(row=row, column=0, columnspan=3, pady=5)

            row += 1


    def delete_appointment(self, appointment_id):
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
        if hasattr(self, "current_frame"):
            self.current_frame.destroy()

        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def show_visit_page(self, user_id, app_id, return_to="main"):
        if "visit_details" in self.pages:
            self.pages["visit_details"].destroy()
            del self.pages["visit_details"]

        visit_details_page = VisitDetails(self, self, user_id, app_id)
        self.pages["visit_details"] = visit_details_page
        visit_details_page.grid(row=0, column=0, sticky="nsew")
        visit_details_page.tkraise()
    
    def show_prescription_page(self, user_id, mode, patient_id, app_id = None):
        prescription_page = IssuePrescription(self, self, mode, user_id, patient_id, app_id)
        self.pages["prescription"] = prescription_page
        prescription_page.grid(row=0, column=0, sticky="nsew")
        prescription_page.tkraise()

    def show_patient_page(self, patient_id, user_id, return_to="main"):
        if "patientpage" in self.pages:
            self.pages["patientpage"].destroy()
            del self.pages["patientpage"]

        patient_page = PatientPage(self, self, user_id, patient_id)
        self.pages["patientpage"] = patient_page
        patient_page.grid(row=0, column=0, sticky="nsew")
        patient_page.tkraise()
    
    def show_open_questionnaire(self, app_id, patient_id, visit_type="first_visit"):
        open_questionnaire_page = openQuestionaire(self, self, app_id, patient_id, visit_type)
        self.pages["openQuestionaire"] = open_questionnaire_page
        open_questionnaire_page.grid(row=0, column=0, sticky="nsew")
        open_questionnaire_page.tkraise()