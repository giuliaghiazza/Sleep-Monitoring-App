import customtkinter as ctk
from PIL import Image
import sqlite3

# Set theme and appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# Dictionary to hold pages
pages = {}

# === Other Pages === #
class HomePage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.setup_gui()

    def setup_gui(self): 
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome, John", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # === Profile Picture ===
        try:
            profile_img = ctk.CTkImage(light_image=Image.open("patientprofile.png"), size=(80, 80))
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
            command=lambda: self.controller.show_page("appointment")
        )
        book_button.grid(row=2, column=0, padx=35, pady=10, sticky="ew")

        data_button = ctk.CTkButton(
            master=self,
            text="📂 My Health Records",
            height=50,
            width=250,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_page("data")
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
            command=lambda: self.controller.show_page("emergency")
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
    def __init__(self, master,controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="🚨 Emergency Contact Page", font=ctk.CTkFont(size=18)).pack(pady=40)

class LoginPage(ctk.CTkFrame):                                                                  #non ho recall ad altre finestre in quanto la prima
    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('gui_database.db')                  #c'è un modo migliore per connettere la classe alle funzioni in Root ma non lo trovo
        self.cursor = self.conn.cursor()
        self.login_gui()

    def login_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # === Labels ===
        login_lable=ctk.CTkLabel(self, 
                                text='Insert Username and Password', 
                                font=('Arial',14),
                                width=300,
                                height=30
                                )
        login_lable.grid(row=1, column=0, padx=20, pady=10)   #numeri da rivedere
        
        # === Fill in fields ===
        self.user_entry=ctk.CTkEntry(self,                                                       #non ho capito perchè. di per se non da errore anche senza self ma senza non posso prendere info dall'utente
                                placeholder_text='Username',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.user_entry.grid(row=2, column=0, pady=(20, 10))   #numeri da rivedere

        self.pass_entry=ctk.CTkEntry(self,
                                placeholder_text='Password',
                                width=200,
                                height=30,
                                font=('Arial',14),
                                show='*'
                                )
        self.pass_entry.grid(row=3, column=0, pady=(20, 10))    #numeri da rivedere

        # === Buttons ===
        login_button = ctk.CTkButton(
            master=self,
            text="Log-in",     #da aggiungere icona se vogliamo metterne una
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            command=self.login_callback
        )
        login_button.grid(row=4, column=0, padx=35, pady=10, sticky="ew")    #numeri da rivedere

        signin_button = ctk.CTkButton(
            master=self,
            text="Sign-in",     #da aggiungere icona se vogliamo metterne una
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_page("Sign-in")
        )
        signin_button.grid(row=5, column=0, padx=35, pady=10, sticky="ew")    #numeri da rivedere, posso fare così per affiancare 2 bottoni?

        # === Outcome Label ===
        self.outcome_label=ctk.CTkLabel(self,
                                        text='',
                                        font=('Arial',12),
                                        width=300,
                                        height=30)      #larghezza come finestra se so che non ho altro sulla riga
        self.outcome_label.grid(row=6, column=0, padx=35, pady=10, sticky="ew")

    #Query database
    def login_callback(self):
        user= (self.user_entry.get(),)
        pw=(self.pass_entry.get(),)

        self.cursor.execute('SELECT nome_utente FROM patients WHERE nome_utente=?', user)
        result = self.cursor.fetchone()

        if result is not None:
            self.cursor.execute('SELECT psw FROM patients WHERE nome_utente=?', user)
            password_try= self.cursor.fetchone()[0]
            if pw==password_try:
                self.cursor.execute('SELECT role FROM patients WHERE nome_utente=?', user)
                role = self.cursor.fetchone()[0]
                if role=='D':
                    self.controller.show_page("home_doc")
                elif role=='T':
                    self.controller.show_page("home_tec")
                elif role=='P':
                    self.controller.show_page("home")
            else:
                self.outcome_label.configure(text='Password incorrect')
                self.outcome_label.configure(text_color='red')
        else:
            self.outcome_label.configure(text='Username incorrect')
            self.outcome_label.configure(text_color='red')

class SigninPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.conn = sqlite3.connect('gui_database.db')
        self.cursor = self.conn.cursor()
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520)
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.signin_gui(scrollable_frame)

    def signin_gui(self, parent):
        # === Header Title ===
        title_label = ctk.CTkLabel(parent, text="Sign In", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

        # === Labels ===
        User_lable=ctk.CTkLabel(parent, 
                                text='Insert Username and Password', 
                                font=('Arial',14),
                                width=300,
                                height=30
                                )
        User_lable.grid(row=1, column=0, pady=(20, 10))
        
        # === Fill in fields ===
        self.user_entry=ctk.CTkEntry(parent,
                                placeholder_text='Username',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.user_entry.grid(row=2, column=0, pady=(20, 10))

        self.pass_entry=ctk.CTkEntry(parent,
                                placeholder_text='Password',
                                width=200,
                                height=30,
                                font=('Arial',14),
                                show='*'
                                )
        self.pass_entry.grid(row=3, column=0, pady=(20, 10))

        # === Labels ===
        Anag_lable=ctk.CTkLabel(parent, 
                                text='Insert Anagraphical data', 
                                font=('Arial',14),
                                width=300,
                                height=30
                                )
        Anag_lable.grid(row=4, column=0, padx=20, pady=10)
        
        # === Fill in fields ===
        self.name_entry=ctk.CTkEntry(parent,
                                placeholder_text='Name',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.name_entry.grid(row=5, column=0, pady=(20, 10))

        self.surname_entry=ctk.CTkEntry(parent,
                                placeholder_text='Surname',
                                width=200,
                                height=30,
                                font=('Arial',14),
                                )
        self.surname_entry.grid(row=6, column=0, pady=(20, 10))

        self.dob_entry=ctk.CTkEntry(parent,
                                placeholder_text='Date of Birth',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.dob_entry.grid(row=7, column=0, pady=(20, 10))

        self.age_entry=ctk.CTkEntry(parent,
                                placeholder_text='Age',
                                width=200,
                                height=30,
                                font=('Arial',14),
                                )
        self.age_entry.grid(row=8, column=0, pady=(20, 10))

        self.cob_entry=ctk.CTkEntry(parent,
                                placeholder_text='City of Birth',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.cob_entry.grid(row=9, column=0, pady=(20, 10))

        self.cor_entry=ctk.CTkEntry(parent,
                                placeholder_text='City of Recidency',
                                width=200,
                                height=30,
                                font=('Arial',14),
                                )
        self.cor_entry.grid(row=10, column=0, pady=(20, 10))

        self.cap_entry=ctk.CTkEntry(parent,
                                placeholder_text='CAP',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        self.cap_entry.grid(row=11, column=0, pady=(20, 10))

        # === Buttons ===
        signin_button = ctk.CTkButton(
            master=parent,
            text="Sign-in",     #da aggiungere icona se vogliamo metterne una
            height=50,
            width=40,
            font=ctk.CTkFont(size=16),
            command=self.signin_callback
            )
        signin_button.grid(row=13, column=0, padx=115, pady=10, sticky="ew")

        # === Outcome Label ===
        self.outcome_label=ctk.CTkLabel(parent,
                                        text='',
                                        font=('Arial',12),
                                        width=300,
                                        height=30)
        self.outcome_label.grid(row=12, column=0, padx=35, pady=10, sticky="ew")
    
    def signin_callback(self):
        user= self.user_entry.get()
        pw= self.pass_entry.get()
        name= self.name_entry.get()
        surname= self.surname_entry.get()
        dob= self.dob_entry.get()
        age= self.age_entry.get()
        cob= self.cob_entry.get()
        cor= self.cor_entry.get()
        cap= self.cap_entry.get()
        
        # if user is not None:
        #     if pw is not None:
        #         if name is not None:
        #            if surname is not None:
        #                if dob is not None:
        #                    if age is not None:
        #                        if cob is not None:
        #                            if cor is not None:
        #                                if cap is not None:
        #                                    self.cursor.execute('INSERT INTO patients(nome_utente,psw,Name,Surname,Dob,Age,City_of_Birth,City_of_Recidency,CAP) VALUES (?,?,?,?,?,?,?,?,?)', user,pw,name,surname,dob,age,cob,cor,cap)
        #                                    self.controller.show_page("log")
        #                                else:
        #                                    self.outcome_label.configure(text='Insert CAP')
        #                                    self.outcome_label.configure(text_color='red')
        #                            else:
        #                                self.outcome_label.configure(text='Insert City_of_Recidency')
        #                                self.outcome_label.configure(text_color='red')
        #                        else:
        #                            self.outcome_label.configure(text='Insert City_of_Birth')
        #                            self.outcome_label.configure(text_color='red')
        #                    else:
        #                        self.outcome_label.configure(text='Insert Age')
        #                        self.outcome_label.configure(text_color='red')
        #                else:
        #                    self.outcome_label.configure(text='Insert Date of Birth')
        #                    self.outcome_label.configure(text_color='red')
        #            else:
        #                self.outcome_label.configure(text='Insert Surname')
        #                self.outcome_label.configure(text_color='red')
        #         else:
        #             self.outcome_label.configure(text='Insert Name')
        #             self.outcome_label.configure(text_color='red')                           
        #     else:
        #         self.outcome_label.configure(text='Insert Password')
        #         self.outcome_label.configure(text_color='red')
        # else:
        #     self.outcome_label.configure(text='Insert Username')
        #     self.outcome_label.configure(text_color='red')

        fields = {
            'Username': user,
            'Password': pw,
            'Name': name,
            'Surname': surname,
            'Date of Birth': dob,
            'Age': age,
            'City of Birth': cob,
            'City of Recidency': cor,
            'CAP': cap
        }

        for label, value in fields.items():
            if not value:
                self.outcome_label.configure(text=f'Insert {label}', text_color='red')
                return  #exits

        self.cursor.execute('''
            INSERT INTO patients(nome_utente, psw, Name, Surname, Dob, Age, City_of_Birth, City_of_Recidency, CAP)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user, pw, name, surname, dob, age, cob, cor, cap))
        self.controller.show_page("log")

class Home_docPage(ctk.CTkFrame):
    def __init__(self, master,controller):
        super().__init__(master)
        self.controller = controller
        self.home_doc_gui()

    def home_doc_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome doctor", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))

class Home_tecPage(ctk.CTkFrame):
    def __init__(self, master,controller):
        super().__init__(master)
        self.controller = controller
        self.home_doc_gui()

    def home_doc_gui(self):
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="Welcome tecnician", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.grid(row=0, column=0, pady=(20, 10))


# === Page Classes ===

class PatientVisualization():
    def show_page(self, page_name):
            for page in self.pages.values():
                page.grid_forget()
            self.pages[page_name].grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    def __init__(self):      # When launching the app
        self.conn = sqlite3.connect('gui_database.db')
        self.cursor = self.conn.cursor()

        # Create main window
        self.root = ctk.CTk()
        self.root.title('Healthcare Portal')
        self.root.configure(fg_color="white")
        self.root.geometry('360x520')
        self.root.resizable(False, False)
        self.root.grid_columnconfigure(0, weight=1)

        # === Pages Dictionary === #
        self.pages = {
            "home": HomePage(self.root, self),
            "appointment": AppointmentPage(self.root, self),
            "data": HealthDataPage(self.root, self),
            "emergency": EmergencyPage(self.root,self),
            "log": LoginPage(self.root, self),
            "Sign-in": SigninPage(self.root, self),
            "home_doc": Home_docPage(self.root, self),
            "home_tec": Home_tecPage(self.root, self),
        }

        self.show_page("log")   #prima era home, se non funziona torno qua
        self.root.mainloop()       
        

# Start the app
PatientVisualization()


#per ogni nuova pagina:
#aggiornare dictionary
#mettere la stessa funzione init per tutte, con master ecc
#far chiamare ad init una def nella stessa classe che descriva la pagina stessa
#se serve chiamare una pagina nuova bisogna passare dal controller