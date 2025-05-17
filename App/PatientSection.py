import customtkinter as ctk
from PIL import Image
import sqlite3

class AppointmentPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="📅 Book Appointment Page", font=ctk.CTkFont(size=18)).pack(pady=40)
        
class HealthDataPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="📂 Health Data Page", font=ctk.CTkFont(size=18)).pack(pady=40)

class EmergencyPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="🚨 Emergency Contact Page", font=ctk.CTkFont(size=18)).pack(pady=40)

class Main(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.setup_gui()
    
    def setup_gui(self): 
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome, John", font=ctk.CTkFont(size=22, weight="bold"))
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
            text="📅 Book Appointment",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("appointment")
        )
        book_button.grid(row=2, column=0, padx=35, pady=10, sticky="ew")

        data_button = ctk.CTkButton(
            master=self,
            text="📂 My Health Records",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_internal_page("data")
        )
        data_button.grid(row=3, column=0, padx=35, pady=10, sticky="ew")

        emergency_button = ctk.CTkButton(
            master=self,
            text="🚨 Emergency Contact",
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
            text="☰ Menu",
            width=100,
            height=35,
            font=ctk.CTkFont(size=14),
            command=lambda: print("Menu opened")
        )
        menu_button.pack()    


# === Patient Pages === #
class Home_patPage(ctk.CTkFrame):
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
            "data": HealthDataPage(self, self),
            "emergency": EmergencyPage(self, self),
        }

        self.show_internal_page("main")