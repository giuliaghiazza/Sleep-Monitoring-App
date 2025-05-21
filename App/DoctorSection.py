import customtkinter as ctk
from PIL import Image
import sqlite3
import datetime

class VisitDetails(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        # Scrollable frame for appointments
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.visitgui(scrollable_frame)

    def visitgui(self, parent):
        parent.grid_columnconfigure(0, weight=0)  # Back button column
        parent.grid_columnconfigure(1, weight=1)  # Main content column

        title_label = ctk.CTkLabel(parent, text="🩺 Visit Details", font=ctk.CTkFont(size=22, weight="bold"))
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

class Manage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.user_id = user_id
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        # Scrollable frame for appointments
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=10, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.managegui(scrollable_frame)

    def managegui(self, parent):
        title_label = ctk.CTkLabel(parent, text="🛠 Manage Page", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=1, pady=(20, 10))

        parent.grid_columnconfigure(0, weight=0)  # Back button column
        parent.grid_columnconfigure(1, weight=1)  # Main content column

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
        title_label = ctk.CTkLabel(parent, text="🩺 Visit Details", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))


class Main(ctk.CTkFrame):   
    def __init__(self, master, controller, user_id=None):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

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
            profile_pic.grid(row=0, column=0, pady=(20, 10), sticky="e")
        except:
            pass

        ctk.CTkLabel(parent, text="Your Appointments 🌞", font=ctk.CTkFont(size=22, weight="bold")).grid(row=1, column=0, columnspan=3, pady=(10, 10))

        # === Filter Buttons ===
        button_config = {
            "height": 45,
            "corner_radius": 3,
            "font": ctk.CTkFont(size=15),
            "hover_color" :"#57cc99",
            "fg_color":"#38a3a5",
            "text_color": "#333"
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

        # Persistent Manage Button (row=1000 to stay always at bottom)
        ctk.CTkButton(
            self.appointments_container,
            text="🛠 Manage Appointments",
            width=180,
            corner_radius=10,
            fg_color="#57cc99",
            hover_color="#38a3a5",
            text_color="black",
            font=ctk.CTkFont(size=14),
            command=lambda: self.controller.show_internal_page("manage")
        ).grid(row=1000, column=0, columnspan=3, pady=(30, 10))

         # === Search Entry ===
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(parent, placeholder_text="Search patient name...", textvariable=self.search_var, width=250)
        search_entry.grid(row=1001, column=0, columnspan=2, pady=(5, 10), padx=5, sticky="e")

        search_button = ctk.CTkButton(
            parent, 
            text="Search patient name...", 
            fg_color="#57cc99",
            hover_color="#38a3a5",
            command=lambda: self.show_appointments("search", user_id, self.search_var.get())
        )
        search_button.grid(row=1001, column=2, pady=(5, 10), padx=5, sticky="w")

    def show_appointments(self, time_slot, user_id, patient_name = None):
        for widget in self.appointments_container.winfo_children():
            grid_info = widget.grid_info()
            if 4 <= int(grid_info.get("row", 0)) < 500:
                widget.destroy()

        # Filter logic
        params = []
        where_clauses = []

        if time_slot in ["today", "tomorrow"]:
            today_str = "2025-05-17" if time_slot == "today" else "2025-05-18"
            where_clauses.append("date(A.slot_tempo) = ?")
            params.append(today_str)
            no_appointments_text = f"No {time_slot} appointments 💤"
        else:
            no_appointments_text = "No appointments available 💤"

        where_clauses.append("A.doctor = ?")
        params.append(user_id)

        time_condition = "WHERE " + " AND ".join(where_clauses)

        if patient_name:
            where_clauses.append("(P.Name LIKE ? OR P.Surname LIKE ?)")
            name_filter = f"%{patient_name,}%"
            params.extend([name_filter, name_filter])

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
                command=lambda vt=appointment_id: self.controller.show_internal_page("visit_details", vt)
            )
            apt_button.grid(row=row, column=0, columnspan=3, pady=5)
            row += 1


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
        self.pages["manage"] = Manage(self, self, self.user_id)
        self.pages["visit_details"] = VisitDetails(self, self, self.user_id)

        self.show_internal_page("main")

    def show_internal_page(self, page_name, *args):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
