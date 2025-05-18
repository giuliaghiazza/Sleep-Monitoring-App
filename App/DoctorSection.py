import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime


class VisitDetails(ctk.CTkFrame):
    def __init__(self, master,controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.visitgui()

    def visitgui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome tecnician", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

class AppointmentPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id = None):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=5, fill="both", expand=True)
        self.Appointment_doc_gui(scrollable_frame, user_id)
        
    def Appointment_doc_gui(self, parent, user_id):
        self.appointments_container = parent
        # === Header Title === #
        title_label = ctk.CTkLabel(parent, text="Your Appointments", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(5, 10))

        title_label = ctk.CTkLabel(parent, text="🌞 Today Appointments", font=ctk.CTkFont(size=15, weight="bold"))
        title_label.grid(row=1, column=0, columnspan=3, pady=(5, 10))

        book_button = ctk.CTkButton(
            master=parent,
            text="Morning",
            height=50,
            width=90,
            font=ctk.CTkFont(size=16),
            command=lambda: self.show_appointments("morning", user_id)
        )
        book_button.grid(row=2, column=0, padx=5, pady=10, sticky="w")

        book_button = ctk.CTkButton(
            master=parent,
            text="Afternoon",
            height=50,
            width=90,
            font=ctk.CTkFont(size=16),
            command=lambda: self.show_appointments("afternoon", user_id)
        )
        book_button.grid(row=2, column=1, padx=5, pady=10, sticky="w")

        book_button = ctk.CTkButton(
            master=parent,
            text="All",
            height=50,
            width=90,
            font=ctk.CTkFont(size=16),
            command=lambda: self.show_appointments("all", user_id)
        )
        book_button.grid(row=2, column=2, padx=5, pady=10, sticky="w")
    
    def show_appointments(self, time_slot, user_id):
        for widget in self.appointments_container.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and int(grid_info.get("row", 0)) > 2:
                widget.destroy()

        today_str = "2025-05-17"

        # Define the time filter condition based on time_slot
        time_condition = ""
        if time_slot == "morning":
            time_condition = "AND time(A.slot_tempo) < '12:00:00'"
            no_appointments_text = "No morning appointments today"
        elif time_slot == "afternoon":
            time_condition = "AND time(A.slot_tempo) >= '12:00:00'"
            no_appointments_text = "No afternoon appointments today"
        else:  # all
            time_condition = ""
            no_appointments_text = "No appointments today"

        # Prepare the SQL query with the time condition
        query = f"""
            SELECT 
                A.slot_tempo, 
                A.visit_type,
                P.Name,
                P.Surname,
                A.appointment_id
            FROM Appointments A
            JOIN Patients P ON A.patient = P.user_id
            WHERE date(A.slot_tempo) = ?
            {time_condition}
            AND A.doctor = ?
        """

        self.cursor.execute(query, (today_str, user_id))
        appointments = self.cursor.fetchall()

        if not appointments:
            no_apt_label = ctk.CTkLabel(self.appointments_container, text=no_appointments_text)
            no_apt_label.grid(row=3, column=0, columnspan=3, pady=20)
            return

        row = 3
        for appointment in appointments:
            time_str = appointment[0].split(' ')[1][:5]
            visit_type = appointment[1]
            self.cursor.execute("""SELECT Visit FROM Visits WHERE visit_code = ?""", (visit_type,))
            visit_name = self.cursor.fetchone()
            visit_name_str = visit_name[0] if visit_name else "Unknown"
            patient_name = f"{appointment[2]} {appointment[3]}"
            appointment_id = appointment[4]
            
            button_text = f"{time_str} | {patient_name} | {visit_name_str}"

            apt_button = ctk.CTkButton(
                self.appointments_container,
                text=button_text,
                width=300,
                command=lambda vt=appointment_id: self.controller.show_internal_page("visit_details", vt)
            )
            apt_button.grid(row=row, column=0, columnspan=3, pady=5)
            row += 1

        

class Documents(ctk.CTkFrame):
    def __init__(self, master, controller, user_id = None):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.documents_doc_gui()
        
    def documents_doc_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Your Appointments", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))


# == Actual Home Page == #
class Main(ctk.CTkFrame):   
    def __init__(self, master,controller):
        super().__init__(master, fg_color = "white")
        self.controller = controller
        self.home_doc_gui()

    def home_doc_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome Doctor", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # === Profile Picture ===
        try:
            profile_img = ctk.CTkImage(light_image=Image.open("App/doctorprofile.png"), size=(150, 150))
            profile_pic = ctk.CTkLabel(self, image=profile_img, text="")
            profile_pic.grid(row=1, column=0, pady=(0, 20))
        except:
            pass

        # === Buttons ===
        book_button = ctk.CTkButton(
            master=self,
            text="📅 Appointment List",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("appointment")
        )
        book_button.grid(row=2, column=0, padx=35, pady=10, sticky="ew")

        data_button = ctk.CTkButton(
            master=self,
            text="📂 My Documents",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("data")
        )
        data_button.grid(row=3, column=0, padx=35, pady=10, sticky="ew")

        # === Bottom Menu ===
        menu_bar = ctk.CTkFrame(self, fg_color="transparent")
        menu_bar.grid(row=5, column=0, pady=20)

        menu_button = ctk.CTkButton(
            master=menu_bar,
            text="☰ Menu",
            width=100,
            height=35,
            font=ctk.CTkFont(size=14),
            command=lambda: print("Menu opened")
        )
        menu_button.pack()    

# == Reference Page == #
class Home_docPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.master = master
        self.controller = controller
        self.user_id = user_id
        print(user_id)
        self.pages = {}  # Don't initialize sub-pages yet

        self.pages["main"] = Main(self, self)
        self.pages["appointment"] = AppointmentPage(self, self, self.user_id)
        self.pages["data"] = Documents(self, self, self.user_id)
        self.pages["visit_details"] = VisitDetails(self, self, self.user_id)

        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
