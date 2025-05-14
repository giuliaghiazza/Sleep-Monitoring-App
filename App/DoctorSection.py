import customtkinter as ctk
from PIL import Image
import sqlite3


class Home_docPage(ctk.CTkFrame):
    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()
            self.pages[page_name].grid(row=1, column=0)
            
    def __init__(self, master,controller):
        super().__init__(master)
        self.controller = controller
        self.home_doc_gui()

    def home_doc_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome doctor", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))