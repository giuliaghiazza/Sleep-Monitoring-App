import customtkinter as ctk
from PIL import Image
import sqlite3
from PatientSection import Home_patPage
from DoctorSection import Home_docPage
from TechnicianSection import Home_tecPage


# Set theme and appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# Dictionary to hold pages
pages = {}

class LoginPage(ctk.CTkFrame):     
    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('App/Database/gui_database.db')   
        self.cursor = self.conn.cursor()
        self.grid_columnconfigure(0, weight=1)

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
        self.user_entry=ctk.CTkEntry(self,                                                     
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
            fg_color="#38a3a5",
            hover_color="#57cc99",
            font=ctk.CTkFont(size=16),
            command=self.login_callback
        )
        login_button.grid(row=4, column=0, padx=35, pady=10)    #numeri da rivedere
 
        signin_button = ctk.CTkButton(
            master=self,
            text="Sign-in",     #da aggiungere icona se vogliamo metterne una
            height=50,
            width=120,
            fg_color="#57cc99",
            hover_color="#38a3a5",
            font=ctk.CTkFont(size=16),
            command=lambda: self.controller.show_page("Sign-in")
        )
        signin_button.grid(row=5, column=0, padx=35, pady=10)    #numeri da rivedere, posso fare così per affiancare 2 bottoni?

        # === Outcome Label ===
        self.outcome_label=ctk.CTkLabel(self,
                                        text='',
                                        font=('Arial',12),
                                        width=300,
                                        height=30)      #larghezza come finestra se so che non ho altro sulla riga
        self.outcome_label.grid(row=6, column=0, padx=35, pady=10)

    #Query database
    def login_callback(self):
        user = (self.user_entry.get(),)
        pw = self.pass_entry.get()

        self.grid_columnconfigure(0, weight=1)

        self.cursor.execute('SELECT username FROM Users WHERE username=?', user)
        result = self.cursor.fetchone()[0]

        if result is not None:
            self.cursor.execute('SELECT psw FROM Users WHERE username=?', user)
            password_try= self.cursor.fetchone()[0]
            if pw==password_try:
                #self.outcome_lable.configure(text='Login Successful, welcome {user[0]}')
                #self.outcome_lable.configure(text_color='green')                           #se lo sto mandando ad un altra pagina non penso serva far vedere sta roba
                self.cursor.execute('SELECT role FROM Users WHERE username=?', user)
                role = self.cursor.fetchone()[0]
                self.cursor.execute('SELECT user_id FROM Users WHERE username=?', user)
                user_id = self.cursor.fetchone()[0]
                if role=='D':
                    self.controller.show_page("home_doc", user_id=user_id)
                elif role=='T':
                    self.controller.show_page("home_tec", user_id=user_id)
                elif role=='P':
                    self.controller.show_page("home_pat", user_id=user_id)
            else:
                self.outcome_label.configure(text='Password incorrect')
                self.outcome_label.configure(text_color='red')
        else:
            self.outcome_label.configure(text='Username incorrect')
            self.outcome_label.configure(text_color='red')

class SigninPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.conn = sqlite3.connect('gui_database.db')
        self.cursor = self.conn.cursor()
        scrollable_frame = ctk.CTkScrollableFrame(self, width=360, height=520, fg_color="white")
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)
        scrollable_frame.grid_columnconfigure(0, weight=0)

        self.signin_gui(scrollable_frame)

    def signin_gui(self, parent):
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
            command= lambda: self.controller.show_page("log")
        )
        back_button.grid(row=0, column=0, padx=(10, 5), pady=(20, 10), sticky="w")

        # === Header Title ===
        title_label = ctk.CTkLabel(
            parent, text="Sign In",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.grid(row=0, column=1, pady=(20, 10), sticky="w")

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
        signin_button.grid(row=13, column=0, padx=115, pady=10)

        # === Outcome Label ===
        self.outcome_label=ctk.CTkLabel(parent,
                                        text='',
                                        font=('Arial',12),
                                        width=300,
                                        height=30)
        self.outcome_label.grid(row=12, column=0, padx=35, pady=10)
    
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

        role = 'P'
        self.cursor.execute('''
            INSERT INTO Users(nome_utente, psw, role)
            VALUES (?, ?, ?)
        ''', (user, pw, role))

        self.cursor.execute('''
            INSERT INTO Patients(Name, Surname, Dob, Age, City_of_Birth, City_of_Recidency, CAP)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user, pw, name, surname, dob, age, cob, cor, cap))
        self.controller.show_page("log")
 

# === Page Classes ===

class App():
    def show_page(self, page_name, user_id = None):
    # Remove existing page if we're re-creating it with user_id
        if user_id is not None and page_name not in self.pages:
            if page_name == "home_doc":
                self.pages[page_name] = Home_docPage(self.root, self, user_id)
            elif page_name == "home_pat":
                self.pages[page_name] = Home_patPage(self.root, self, user_id)
            elif page_name == "home_tec":
                self.pages[page_name] = Home_tecPage(self.root, self, user_id)

        for page in self.pages.values():
            page.grid_forget()

        # Create page with user_id if neede
        page = self.pages.get(page_name)

        if hasattr(page, "receive_user_id"):
            page.receive_user_id(user_id)

        page.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    def __init__(self):      # When launching the app
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()

        # Create main window
        self.root = ctk.CTk()
        self.root.title('Healthcare Portal')
        self.root.configure(fg_color="white")
        self.root.geometry('750x550')
        self.root.resizable(False, False)
        self.root.grid_columnconfigure(0, weight=1)

        # === Pages Dictionary === #
        self.pages = {
            "log": LoginPage(self.root, self),
            "Sign-in": SigninPage(self.root, self),
        }

        self.show_page("log")   #prima era home, se non funziona torno qua
        self.root.mainloop()       
        

# Start the app
App()


#per ogni nuova pagina:
#aggiornare dictionary
#mettere la stessa funzione init per tutte, con master ecc
#far chiamare ad init una def nella stessa classe che descriva la pagina stessa
#se serve chiamare una pagina nuova bisogna passare dal controller