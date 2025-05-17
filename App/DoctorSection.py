import customtkinter as ctk
from PIL import Image
import sqlite3

class AppointmentPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('gui_database.db')
        self.cursor = self.conn.cursor()
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520)
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.Appointment_doc_gui(scrollable_frame)
        
    def Appointment_doc_gui(self, parent):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Your Appointments", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        title_label = ctk.CTkLabel(self, text="Today Appointments", font=ctk.CTkFont(size=15, weight="bold"))
        title_label.grid(row=1, column=0, pady=(20, 10))

        title_label = ctk.CTkLabel(self, text="Today Appointments", font=ctk.CTkFont(size=15, weight="bold"))
        title_label.grid(row=2, column=0, pady=(20, 10))

class Documents(ctk.CTkFrame):
    def __init__(self, master, controller):
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
            command=lambda: self.show_internal_page("data")
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
    def show_internal_page(self, page_name):
            for page in self.pages.values():
                page.grid_forget()
            self.pages[page_name].grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.master = master

        self.pages = {
            "main": Main(self, self),
            "appointment": AppointmentPage(self, self),
            "data": Documents(self, self)
        }

        self.show_internal_page("main")