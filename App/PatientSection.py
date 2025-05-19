import customtkinter as ctk
from PIL import Image
import sqlite3

# Dictionary to hold pages
pages = {}
doc_avail_vect=None
#doc_sel='Select doctor'
# === Other Pages === #
class Main(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
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

class AppointmentPage(ctk.CTkFrame):
    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.controller = controller
        self.user_id = user_id
        self.setup_gui(self.user_id)

    def setup_gui(self, user_id): 
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="📅 Book Appointment Page", font=ctk.CTkFont(size=18))
        title_label.grid(row=0, column=0, pady=(20, 10))
        self.conn = sqlite3.connect('App/Database/gui_database.db')
        self.cursor = self.conn.cursor()
        
        #self.cursor.execute('SELECT DISTINCT doctor FROM appointment WHERE patient=?', (user,)) #user da passare
        self.cursor.execute('SELECT DISTINCT slot_tempo FROM Appointments WHERE dispo=1')
        n_availability_vect=self.cursor.fetchall()
        n_availability= len(n_availability_vect)

        self.selected_index=None
        self.selected_index1=None
        self.selected_index2=None
        
        #tab prenotazione
        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        self.tabview.add("Availability")
        self.tabview.add("Doctor")
        self.tabview.add("Submit")
        self.tabview.tab("Availability").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Doctor").grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.tabview.tab("Availability"), label_text="Select time slot")
        self.scrollable_frame.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_radiobut = []
        self.radio_var = ctk.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.scrollable_frame, text="Available slots")
        for i in range(n_availability):
            slot_text=n_availability_vect[i][0]
            radio_button = ctk.CTkRadioButton(master=self.scrollable_frame, variable=self.radio_var, value=i, text=slot_text)
            radio_button.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_radiobut.append(radio_button)
        slot_sel, doc_avail= self.get_selected_text()

        ## QUA MANCA METTERE I DOTTORI DISPONIBILI, BISOGNA INVERTIRE CON I TIME SLOT
        self.scrollable_frame1 = ctk.CTkScrollableFrame(self.tabview.tab("Doctor"), label_text="Select Doctor")
        self.scrollable_frame1.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame1.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_radiobut1 = []
        self.radio_var1 = ctk.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.scrollable_frame1, text="Available Doctors")
        if doc_avail_vect is not None:
            for j in range(doc_avail):
                slot_text_doc=doc_avail_vect[j][0]
                radio_button1 = ctk.CTkRadioButton(master=self.scrollable_frame1, variable=self.radio_var1, value=j, text=slot_text_doc)
                radio_button1.grid(row=j+2, column=0, padx=10, pady=(0, 20))
                self.scrollable_frame_radiobut1.append(radio_button1)
            doc_sel= self.get_selected_text1()

        # === Buttons ===
        confirm_button = ctk.CTkButton(
            master=self.tabview.tab("Submit"),
            text="Book appointment",
            height=30,
            width=80,
            font=ctk.CTkFont(size=16),
            command=lambda: self.conferma(slot_sel, doc_sel, user_id)
        )
        confirm_button.grid(row=3, column=2, padx=35, pady=10, sticky="ew")

    #     print_button = ctk.CTkButton(
    #         master=self.tabview.tab("Submit"),
    #         text="Print receipt",
    #         height=30,
    #         width=80,
    #         font=ctk.CTkFont(size=16),
    #         #command=lambda: self.controller.show_page("data") tanto non è chge devo stampare davvero
    #     )
    #     print_button.grid(row=3, column=0, padx=35, pady=10, sticky="ew")

    #     # === Labels ===
    #     if self.selected_index is not None:
    #         rec1_lable=ctk.CTkLabel(self.tabview.tab("Submit"), 
    #                                 text=slot_sel, 
    #                                 font=('Arial',14),
    #                                 width=80,
    #                                 height=20
    #                                 )
    #         rec1_lable.grid(row=1, column=0, padx=20, pady=10, columnspan=3)
    #         confirm_button.configure(state="normal")
    #     else:
    #         rec1_lable=ctk.CTkLabel(self.tabview.tab("Submit"), 
    #                                 text='Select a time slot', 
    #                                 font=('Arial',14),
    #                                 width=80,
    #                                 height=20
    #                                 )
    #         rec1_lable.grid(row=1, column=0, padx=20, pady=10, columnspan=3)
    #         confirm_button.configure(state="disabled")
        
    #     if doc_avail_vect is not None:
    #         rec2_lable=ctk.CTkLabel(self.tabview.tab("Submit"), 
    #                                 text=doc_sel, 
    #                                 font=('Arial',14),
    #                                 width=80,
    #                                 height=20
    #                                 )
    #         rec2_lable.grid(row=2, column=0, padx=20, pady=10, columnspan=3)
    #         print_button.configure(state="normal")
    #     else:
    #         rec2_lable=ctk.CTkLabel(self.tabview.tab("Submit"), 
    #                                 text='Select a doctor', 
    #                                 font=('Arial',14),
    #                                 width=80,
    #                                 height=20
    #                                 )
    #         rec2_lable.grid(row=2, column=0, padx=20, pady=10, columnspan=3)
    #         print_button.configure(state="disabled")
        


    #     #per visualizzare visite già prenotate
    #     self.cursor.execute('SELECT n_booked FROM Patients WHERE user_id=?', user_id)
    #     n_booked_tup= self.cursor.fetchone()
    #     n_booked = int(n_booked_tup[0])
    #     n_book=len(n_booked_tup)
    #     self.cursor.execute('SELECT appointment_id, slot_tempo, doctor FROM Appointments WHERE patient=?', user_id)
    #     visit_booked=self.cursor.fetchall()

    #     # === Elenco visite prenotate ===
    #     self.scrollable_frame3 = ctk.CTkScrollableFrame(self, label_text="Your booked appointment")
    #     self.scrollable_frame3.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)                                            #qua sostituire la composizione di lable a più informazioni
    #     self.scrollable_frame3.grid_columnconfigure(0, weight=1)
    #     for i in range(n_booked):
    #         visit_x=visit_booked[i][0]
    #         book_lable=ctk.CTkLabel(master=self.scrollable_frame3, 
    #                             text=visit_x,
    #                             font=('Arial',14),
    #                             width=80,
    #                             height=20
    #                             )
    #         book_lable.grid(row=i+1, column=0, padx=20, pady=10, columnspan=3)

    #     # === Filtro eliminazione visita ===
    #     self.scrollable_frame4 = ctk.CTkScrollableFrame(self, label_text="Filter for doctor and time slot", width=500)
    #     self.scrollable_frame4.grid(row=1, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
    #     self.scrollable_frame4.grid_columnconfigure(0, weight=1)
    #     #del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
    #     #                        text='Search for visit to forfeit', 
    #     #                        font=('Arial',14),
    #     #                        width=300,
    #     #                        height=30
    #     #                        )
    #     #del_lable.grid(row=1, column=0, padx=20, pady=10, columnspan=2)
    #     data_del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
    #                             text='Data of undesired visit', 
    #                             font=('Arial',11),
    #                             width=300,
    #                             height=30
    #                             )
    #     data_del_lable.grid(row=0, column=0, padx=20, pady=10)
    #     doc_del_lable=ctk.CTkLabel(master=self.scrollable_frame4, 
    #                             text='Doctor of undesired visit', 
    #                             font=('Arial',11),
    #                             width=300,
    #                             height=30
    #                             )
    #     doc_del_lable.grid(row=0, column=2, padx=20, pady=10)

    #     self.cursor.execute('SELECT slot_tempo FROM Appointments WHERE patient=?', user_id)
    #     hours=self.cursor.fetchall()
    #     self.combobox_1 = ctk.CTkComboBox(master=self.scrollable_frame4,
    #                                     values = [str(hour[0]) for hour in hours])
    #     self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
    #     self.combobox_1.set("")
    #     self.cursor.execute('SELECT doctor FROM Appointments WHERE patient=?', user_id)
    #     doct=self.cursor.fetchall()
    #     self.combobox_2 = ctk.CTkComboBox(master=self.scrollable_frame4,
    #                                     values = [str(doc_str[0]) for doc_str in doct])
    #     self.combobox_2.grid(row=1, column=2, padx=20, pady=(10, 10))
    #     self.combobox_2.set("")

    #     # === Elenco visite filtrate tra le possibili da eliminare ===
    #     self.scrollable_frame2 = ctk.CTkScrollableFrame(self, label_text="Select visit to forfeit")
    #     self.scrollable_frame2.grid(row=2, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
    #     self.scrollable_frame2.grid_columnconfigure(1, weight=1)
    #     self.scrollable_frame_radiobut2 = []
    #     self.radio_var2 = ctk.IntVar(value=0)
    #     self.label_radio_group2 = ctk.CTkLabel(master=self.scrollable_frame2, text="Available visits")
    #     if len(visit_booked)>0:
    #         for i in range(n_book):
    #             booked_round = f"Appointment Code: {visit_booked[i][0]}, Time: {visit_booked[i][1]}, Doctor: {visit_booked[i][2]}"
    #             radio_button1 = ctk.CTkRadioButton(master=self.scrollable_frame2, variable=self.radio_var2, value=i, text=booked_round)
    #             radio_button1.grid(row=i, column=0, padx=10, pady=(0, 20))
    #             self.scrollable_frame_radiobut2.append(radio_button1)
    #         visit_sel= self.get_selected_text2()
    #         code= self.get_codice_appuntamento(visit_sel)
    #     else:
    #         self.label_radio_group2 = ctk.CTkLabel(master=self.scrollable_frame2, text="No visit booked")
    #         self.label_radio_group2.grid(row=1, column=0, padx=10, pady=(0, 20), columnspan=3)

    #     if len(visit_booked)>0:
    #         eliminate_button = ctk.CTkButton(
    #             master=self.scrollable_frame2,
    #             text="Forfeit selected appointment",
    #             height=30,
    #             width=80,
    #             font=ctk.CTkFont(size=12),
    #             command=lambda: self.eliminate(code)
    #         )
    #         eliminate_button.grid(row=n_book+3, column=5, padx=35, pady=10, sticky="ew")
    #         eliminate_button.configure(state="normal")
    #     else:
    #         eliminate_button = ctk.CTkButton(
    #             master=self.scrollable_frame2,
    #             text="Forfeit selected appointment",
    #             height=30,
    #             width=80,
    #             font=ctk.CTkFont(size=12),
    #             command=lambda: self.eliminate(code)
    #         )
    #         eliminate_button.grid(row=n_book+3, column=5, padx=35, pady=10, sticky="ew")
    #         eliminate_button.configure(state="disabled")


    #     menu_bar = ctk.CTkFrame(self, fg_color="transparent")
    #     menu_bar.grid(row=3, column=5, pady=20)
    #     menu_button = ctk.CTkButton(
    #         master=menu_bar,
    #         text="☰ Menu",
    #         width=100,
    #         height=35,
    #         font=ctk.CTkFont(size=14),
    #         command=self.menu_callback
    #     )
    #     menu_button.grid(row=3, column=5, padx=10, pady=(0, 20))

    def conferma(self, slot_sel, doc_sel, user, user_id):
        self.cursor.execute('SELECT appointment_id FROM Appointments WHERE slot_tempo=?  AND doctor=?', slot_sel, doc_sel)
        codice=self.cursor.fetchone()
        self.cursor.execute('UPDATE Appointments (patient, dispo) VALUES(?, 0) WHERE appointment_id = ?;', user_id, codice)              #con idea che parto con tabella gia piena con slot ora e dottore, ma dispo=1

    # def get_codice_appuntamento(self, visit_sel): #metodo elaborazione stringa
    #     if visit_sel:
    #         parts = visit_sel.split(",")
    #         codice = parts[0].split(":")[1].strip()
    #         return codice
    #     return None

    # def eliminate(self,code):
    #     self.cursor.execute("""
    #                         UPDATE Appointments
    #                         patient = NULL,
    #                         dispo=1
    #                         WHERE appointment_id = ?;
    #                         """,code)

    def get_selected_text(self):
        selected_index = self.radio_var.get()
        if self.selected_index is not None:
            slot_sel = self.scrollable_frame_radiobut[selected_index].cget("text")
            self.cursor.execute('SELECT DISTINCT doctor FROM Appointments WHERE dispo= 1 AND slot_tempo=?',slot_sel)
            doc_avail_vect=self.cursor.fetchall()
            doc_avail= len(doc_avail_vect)
            return slot_sel, doc_avail
        else:
            return None, None
    
    def get_selected_text1(self):
        if self.selected_index1 is not None:
            selected_index1 = self.radio_var1.get()
            doc_sel = self.scrollable_frame_radiobut1[selected_index1].cget("text")
            return doc_sel
        else:
            return None
        
    def get_selected_text2(self):
        if self.selected_index2 is not None:
            selected_index2 = self.radio_var2.get()
            visit_sel = self.scrollable_frame_radiobut2[selected_index2].cget("text")
            return visit_sel
        else:
            return None

    # def menu_callback(self):
    #     SIDEBAR_WIDTH=250
    #     self.sidebar_container = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
    #     self.sidebar_container.grid(row=0, column=0, sticky="ns", rowspan=8)
    #     self.sidebar_container.grid_rowconfigure(0, weight=1)
    #     self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
    #     self.navigation_frame.grid(row=0, column=0, sticky="nsew", rowspan=8)
    #     self.navigation_frame.grid_rowconfigure(4, weight=1)

    #     self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Menu",
    #                                                          compound="left", font=ctk.CTkFont(size=15, weight="bold"))
    #     self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
    #     self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Manage Appointment",
    #                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
    #                                                 anchor="w", command=self.home_button_event, width=SIDEBAR_WIDTH)
    #     self.home_button.grid(row=1, column=0, sticky="ew")
    #     self.frame_2_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Health data record",
    #                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
    #                                                    anchor="w", command=self.frame_2_button_event, width=SIDEBAR_WIDTH)
    #     self.frame_2_button.grid(row=2, column=0, sticky="ew")
    #     self.frame_3_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Emergency communications",
    #                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
    #                                                    anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
    #     self.frame_3_button.grid(row=3, column=0, sticky="ew")
    #     self.frame_4_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Log out",
    #                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
    #                                                    anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
    #     self.frame_4_button.grid(row=5, column=0, sticky="sew")

    # def select_frame_by_name(self, name):
    #     # set button color for selected button
    #     self.home_button.configure(fg_color=("gray75", "gray25") if name == "Manage Appointment" else "transparent")
    #     self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Health data record" else "transparent")
    #     self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "Emergency communications" else "transparent")

    #     # show selected frame
    #     if name == "Manage Appointment":
    #         self.controller.show_internal_page("appointment")
    #         self.close_sidebar()
    #     if name == "Health data record":
    #         self.controller.show_internal_page("data")
    #         self.close_sidebar()
    #     if name == "Emergency communications":
    #         self.controller.show_internal_page("emergency")
    #         self.close_sidebar()

    # def home_button_event(self):
    #     self.select_frame_by_name("Manage Appointment")

    # def frame_2_button_event(self):
    #     self.select_frame_by_name("Health data record")

    # def frame_3_button_event(self):
    #     self.select_frame_by_name("Emergency communications")

    # def change_appearance_mode_event(self, new_appearance_mode):
    #     ctk.set_appearance_mode(new_appearance_mode)

    # def close_sidebar(self):    #la rimuove dopo che ho scelto una pagina
    #     self.navigation_frame.grid_remove()  # Nascondi il frame
    #     self.sidebar_container.grid_remove()
    #     self.grid_columnconfigure(0, weight=0)
        

        
class HealthDataPage(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="📂 Health Data Page", font=ctk.CTkFont(size=18)).pack(pady=40)

class EmergencyPage(ctk.CTkFrame):
    def __init__(self, master,controller, user_id):
        super().__init__(master)
        self.user_id = user_id
        self.controller = controller
        self.setup_gui()

    def setup_gui(self, user_id): 
        # === Header Title ===
        title_label = ctk.CTkLabel(self, text="🚨 Patient-clinic contacts", font=ctk.CTkFont(size=18))
        title_label.grid(row=0, column=0, pady=(20, 10), columnspan=3)
        self.conn = sqlite3.connect('gui_database.db')
        self.cursor = self.conn.cursor()

        self.tabview = ctk.CTkTabview(self, width=250, height=300)
        self.tabview.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Anagraphic data")
        self.tabview.add("Night related data")
        self.tabview.add("Confirm")
        self.tabview.tab("Anagraphic data").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Night related data").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Confirm").grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.tabview.tab("Anagraphic data"), label_text="Check your anagraphic data")
        self.scrollable_frame.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.cursor.execute('SELECT Name FROM patients WHERE user_id=?', user_id)         #anche qua va capito come passarlo poi in implementazione reale
        nam=self.cursor.fetchone()
        an_var = ctk.StringVar(value=nam)
        an_lable=ctk.CTkLabel(master=self.scrollable_frame, 
                                text='Name:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        an_lable.grid(row=0, column=0, padx=20, pady=10, sticky="sw")
        an_entry=ctk.CTkEntry(master=self.scrollable_frame,
                                textvariable=an_var,
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        an_entry.grid(row=1, column=0, pady=(20, 10))

        self.cursor.execute('SELECT Surname FROM patients WHERE user_id=?', user_id)
        nam1=self.cursor.fetchone()
        an1_var = ctk.StringVar(value=nam1)
        an1_lable=ctk.CTkLabel(master=self.scrollable_frame, 
                                text='Surname:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        an1_lable.grid(row=2, column=0, padx=20, pady=10, sticky="sw")
        an1_entry=ctk.CTkEntry(master=self.scrollable_frame,
                                textvariable=an1_var,
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        an1_entry.grid(row=3, column=0, pady=(20, 10))

        self.cursor.execute('SELECT Codice_Fiscale FROM patients WHERE user_id=?', user_id)
        nam2=self.cursor.fetchone()
        an2_var = ctk.StringVar(value=nam2)
        an2_lable=ctk.CTkLabel(master=self.scrollable_frame, 
                                text='Codice Fiscale:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        an2_lable.grid(row=4, column=0, padx=20, pady=10, sticky="sw")
        an2_entry=ctk.CTkEntry(master=self.scrollable_frame,
                                textvariable=an2_var,
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        an2_entry.grid(row=5, column=0, pady=(20, 10))

        self.cursor.execute('SELECT City_of_Recidency FROM patients WHERE user_id=?', user_id)
        nam3=self.cursor.fetchone()
        an3_var = ctk.StringVar(value=nam3)
        an3_lable=ctk.CTkLabel(master=self.scrollable_frame, 
                                text='Città di residenza:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        an3_lable.grid(row=6, column=0, padx=20, pady=10, sticky="sw")
        an3_entry=ctk.CTkEntry(master=self.scrollable_frame,
                                textvariable=an3_var,
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        an3_entry.grid(row=7, column=0, pady=(20, 10))

        self.cursor.execute('SELECT Province_of_Recidency FROM patients WHERE user_id=?', user_id)
        nam4=self.cursor.fetchone()
        an4_var = ctk.StringVar(value=nam4)
        an4_lable=ctk.CTkLabel(master=self.scrollable_frame, 
                                text='Provincia di residenza:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        an4_lable.grid(row=8, column=0, padx=20, pady=10, sticky="sw")
        an4_entry=ctk.CTkEntry(master=self.scrollable_frame,
                                textvariable=an4_var,
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        an4_entry.grid(row=9, column=0, pady=(20, 10))

        self.scrollable_frame1 = ctk.CTkScrollableFrame(self.tabview.tab("Night related data"), label_text="Insert night related data")
        self.scrollable_frame1.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame1.grid_columnconfigure(0, weight=1)
        nig_lable=ctk.CTkLabel(master=self.scrollable_frame1, 
                                text='cosa ci metto dentro?:', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        nig_lable.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

        prob_entry=ctk.CTkEntry(self.tabview.tab("Confirm"),
                                placeholder_text='Describe any problems encountered during nigth',
                                width=200,
                                height=30,
                                font=('Arial',14)
                                )
        prob_entry.grid(row=0, column=0, pady=(20, 10),columnspan=2)
        con_button = ctk.CTkButton(
            self.tabview.tab("Confirm"),
            text="Send module",
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            command=self.send_module  
        )
        con_button.grid(row=1, column=1, padx=35, pady=10, sticky="nsew")

        #per oscurare tabella
        self.overlay = ctk.CTkFrame(self, width=250, height=300, fg_color="grey")
        self.overlay.place_forget()  # Nascondi inizialmente
        self.overlay.grid_propagate(False)

        #self.scrollable_frame2 = ctk.CTkScrollableFrame(self, label_text="", width=400)
        #self.scrollable_frame2.grid(row=1, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        #self.scrollable_frame2.grid_columnconfigure(0, weight=1)
        self.day_lable=ctk.CTkLabel(master=self, 
                                text='', 
                                font=('Arial',24),
                                width=500,
                                height=200
                                )
        self.day_lable.grid(row=1, column=3, padx=20, pady=10, sticky="nsew")

        menu_bar = ctk.CTkFrame(self, fg_color="transparent")
        menu_bar.grid(row=2, column=3, pady=20)
        menu_button = ctk.CTkButton(
            master=menu_bar,
            text="☰ Menu",
            width=100,
            height=35,
            font=ctk.CTkFont(size=14),
            command=self.menu_callback
        )
        menu_button.grid(row=2, column=4, padx=10, pady=(0, 20))

        self.scrollable_frame2 = ctk.CTkScrollableFrame(self, label_text="Emergency contacts")
        self.scrollable_frame2.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        self.scrollable_frame2.grid_columnconfigure(0, weight=1)
        doc_phone_lable=ctk.CTkLabel(master=self.scrollable_frame2, 
                                text='Choose doctor to contat', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        doc_phone_lable.grid(row=0, column=0, padx=20, pady=10, sticky="sw")

        self.combobox_1 = ctk.CTkComboBox(master=self.scrollable_frame2,
                                        values = [str(hour[0]) for hour in hours])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.combobox_1.set("")
        doc_phone_button = ctk.CTkButton(
            master=self.scrollable_frame2,
            text="Call",
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            #command=self.send_module  
        )
        doc_phone_button.grid(row=2, column=0, padx=35, pady=10, sticky="nsew")

        tec_phone_lable=ctk.CTkLabel(master=self.scrollable_frame2, 
                                text='Choose technician to contact', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        tec_phone_lable.grid(row=0, column=2, padx=20, pady=10, sticky="sw")

        self.combobox_2 = ctk.CTkComboBox(master=self.scrollable_frame2,
                                        values = [str(hour[0]) for hour in hours])
        self.combobox_2.grid(row=1, column=2, padx=20, pady=(10, 10))
        self.combobox_2.set("")
        tec_phone_button = ctk.CTkButton(
            master=self.scrollable_frame2,
            text="Call",
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            #command=self.send_module  
        )
        tec_phone_button.grid(row=2, column=2, padx=35, pady=10, sticky="nsew")

        self.scrollable_frame3 = ctk.CTkScrollableFrame(self, label_text="E-mail contacts")
        self.scrollable_frame3.grid(row=2, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew", columnspan=3)
        self.scrollable_frame3.grid_columnconfigure(0, weight=1)
        doc_mail_lable=ctk.CTkLabel(master=self.scrollable_frame3, 
                                text='Choose doctor to contat', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        doc_mail_lable.grid(row=0, column=0, padx=20, pady=10, sticky="sw")

        self.combobox_1 = ctk.CTkComboBox(master=self.scrollable_frame3,
                                        values = [str(hour[0]) for hour in hours])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.combobox_1.set("")
        doc_mail_button = ctk.CTkButton(
            master=self.scrollable_frame3,
            text="Call",
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            #command=self.send_module  
        )
        doc_mail_button.grid(row=2, column=0, padx=35, pady=10, sticky="nsew")

        tec_mail_lable=ctk.CTkLabel(master=self.scrollable_frame3, 
                                text='Choose technician to contat', 
                                font=('Arial',11),
                                width=300,
                                height=30
                                )
        tec_mail_lable.grid(row=0, column=2, padx=20, pady=10, sticky="sw")

        self.combobox_2 = ctk.CTkComboBox(master=self.scrollable_frame3,
                                        values = [str(hour[0]) for hour in hours])
        self.combobox_2.grid(row=1, column=2, padx=20, pady=(10, 10))
        self.combobox_2.set("")
        tec_mail_button = ctk.CTkButton(
            master=self.scrollable_frame3,
            text="Call",
            height=50,
            width=120,
            font=ctk.CTkFont(size=16),
            #command=self.send_module  
        )
        tec_mail_button.grid(row=2, column=2, padx=35, pady=10, sticky="nsew")


    
    def send_module(self):
        """Oscura la TabView."""
        self.overlay.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")   #da migliorare solo se vogliamo farla semitrasparente al posto di gray poche righe sopra
        self.day_lable.configure(text="Today questionnaire alredy submitted \n come back domorrow")

    def menu_callback(self):
        SIDEBAR_WIDTH=250
        self.sidebar_container = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.sidebar_container.grid(row=0, column=0, sticky="ns", rowspan=8)
        self.sidebar_container.grid_rowconfigure(0, weight=1)
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, width=SIDEBAR_WIDTH)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew", rowspan=8)
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Menu",
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Manage Appointment",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                    anchor="w", command=self.home_button_event, width=SIDEBAR_WIDTH)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.frame_2_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Health data record",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_2_button_event, width=SIDEBAR_WIDTH)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")
        self.frame_3_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Emergency communications",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        self.frame_4_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Log out",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                       anchor="w", command=self.frame_3_button_event, width=SIDEBAR_WIDTH)
        self.frame_4_button.grid(row=5, column=0, sticky="sew")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "Manage Appointment" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Health data record" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "Emergency communications" else "transparent")

        # show selected frame
        if name == "Manage Appointment":
            self.controller.show_internal_page("appointment")
            self.close_sidebar()
        if name == "Health data record":
            self.controller.show_internal_page("data")
            self.close_sidebar()
        if name == "Emergency communications":
            self.controller.show_internal_page("emergency")
            self.close_sidebar()

    def home_button_event(self):
        self.select_frame_by_name("Manage Appointment")

    def frame_2_button_event(self):
        self.select_frame_by_name("Health data record")

    def frame_3_button_event(self):
        self.select_frame_by_name("Emergency communications")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def close_sidebar(self):    #la rimuove dopo che ho scelto una pagina
        self.navigation_frame.grid_remove()  # Nascondi il frame
        self.sidebar_container.grid_remove()
        self.grid_columnconfigure(0, weight=0)

        


# == Reference Page == #
class Home_patPage(ctk.CTkFrame):

    def __init__(self, master, controller, user_id):
        super().__init__(master, fg_color="white")
        self.master = master
        self.user_id = user_id

        self.pages = {
            "main": Main(self, self, self.user_id),
            "appointment": AppointmentPage(self, self, self.user_id),
            # "data": HealthDataPage(self, self, self.user_id),
            # "emergency": EmergencyPage(self, self, self.user_id),
        }

        print(self.user_id)
        self.show_internal_page("main")

    def show_internal_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()
        self.pages[page_name].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

