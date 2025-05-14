import customtkinter as ctk
import sqlite3

class LoginApp():
    def __init__(self):      #ciò che faccio quando lancio l'applicazione
        self.conn=sqlite3.connect('gui_database.db')
        self.cursor=self.conn.cursor()
        
        #creo window su cui metto widgets
        self.root= ctk.CTk()
        self.root.title('Login')   #nome della finestra
        self.root.geometry('300x300')    #do dimensioni della finestra prima passo X poi la Y
        self.setup_gui()                 #assegno metodo alla classe che è la finestra in modo tale da associarle tutti gli altri gadget
        self.root.mainloop()             #continua a frf andare l'applicazione fino a che non succede qualcosa
        
    def setup_gui(self):
        self.login_lable=ctk.CTkLabel(self.root, text='Insert Username and Password', font=('Arial',14),
                                     width=300, height=30)   #definisco una lable, figlia della finestra, il primo passato è il genitore poi ho anche le grandezze in pixel
        self.login_lable.place(x=0,y=30)

        self.user_entry=ctk.CTkEntry(self.root, placeholder_text='Username', width=200, height=30, font=('Arial',14))
        self.user_entry.place(x=50,y=90)
        self.pass_entry=ctk.CTkEntry(self.root, placeholder_text='Password', width=200, height=30, font=('Arial',14), show='*')
        self.pass_entry.place(x=50,y=135)

        self.login_button=ctk.CTkButton(self.root, text='Login', width=100, height=30, font=('Arial',14), hover=True,
                                       command=self.login_callback)  #scelgo cos afar succedere quando premo il bottone usando un callback
        self.login_button.place(x=100,y=180)

        self.outcome_lable=ctk.CTkLabel(self.root, text='', font=('Arial',12),width=300, height=30)      #larghezza come finestra se so che non ho altro sulla riga
        self.outcome_lable.place(x=50,y=240)

    def login_callback(self):
        user= (self.user_entry.get(),)
        pw=(self.pass_entry.get(),)  #per salvare i dati come tuple in modo da poterli poi salvare direttamente così

        self.cursor.execute('SELECT nome_utente FROM patients WHERE nome_utente=?', user) #? è placeholder per l'argomento successivo quando devo passare una variabile
        result = self.cursor.fetchone()

        if result is not None:
            self.cursor.execute('SELECT psw FROM patients WHERE nome_utente=?', user)
            password_try= self.cursor.fetchone()[0]  #per estrarre il primo elemento dal double
            if pw==password_try:
                self.outcome_lable.configure(text='Login Successful, welcome {user[0]}') #per fare modifiche in un widget già creato
                self.outcome_lable.configure(text_color='green')           #noi dovremo trovare una palette scaricare i codici ash e usare quella per avere i bottoni coi colori in palette e sempre uguali usando il codice
                self.root= ctk.CTk()
                self.root.title('patient interface')   #nome della finestra
                self.root.geometry('300x300')    #do dimensioni della finestra prima passo X poi la Y
                self.setup_gui_user_int()                 #assegno metodo alla classe che è la finestra in modo tale da associarle tutti gli altri gadget
                self.root.mainloop()
            else:
                self.outcome_lable.configure(text='Password incorrect') #per fare modifiche in un widget già creato
                self.outcome_lable.configure(text_color='red')
        else:
            self.outcome_lable.configure(text='Username incorrect') #per fare modifiche in un widget già creato
            self.outcome_lable.configure(text_color='red')
    def setup_gui_user_int(self):
        self.book_button = ctk.CTkButton(
        text="📅 Book Appointment",
        height=50,
        font=ctk.CTkFont(size=16),
        #command=lambda: show_page("appointment")
        )
        self.book_button.place(x=0,y=30)
        #book_button.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

LoginApp()