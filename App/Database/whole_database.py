import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()
# Find and drop all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()

for table_name in tables:
    table = table_name[0]
    if table == 'sqlite_sequence':
        continue  # skip special system table
    print(f"Dropping table: {table}")
    c.execute(f"DROP TABLE IF EXISTS '{table}'")

# Users Tables
c.execute("""CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    psw VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at DATETIME
    )"""     
    )

c.execute("""CREATE TABLE IF NOT EXISTS Doctors(
          user_id INTEGER PRIMARY KEY,
          Name VARCHAR(30) NOT NULL,
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16) NOT NULL,
          DoB DATE,
          Gender varchar,
          Age INTEGER CHECK(Age>=0),
          Specialty varchar,
          Unit VARCHAR(30),
          profilepic PATH,
          email varchar, -- emergency contact
          phone integer, -- emergency contact
          FOREIGN KEY (user_id) REFERENCES Users(user_id)
          )
          """)
#A system for direct messages could be implemented


c.execute("""CREATE TABLE IF NOT EXISTS Patients(
          user_id INTEGER PRIMARY KEY,          
          Name VARCHAR(30),
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16),
          DoB text,
          Gender varchar,
          Age INTEGER CHECK(Age>=0),
          City_of_Birth VARCHAR(20),
          Province_of_Birth CHAR(2),
          City_of_Recidency VARCHAR(20),
          Province_of_Recidency CHAR(2),
          CAP INTEGER,
          n_booked INTEGER DEFAULT '0',
          Diagnosis varchar,
          Theraphy varchar, 
          profilepic PATH,
          assigned_doctor integer,
          FOREIGN KEY (user_id) REFERENCES Users(user_id),
          FOREIGN KEY (assigned_doctor) REFERENCES Doctors(user_id)
          )
          """)
# All of the profiles pictures should be added to the tables as a filepath

c.execute("""CREATE TABLE IF NOT EXISTS Technicians(
          user_id INTEGER PRIMARY KEY,
          Name VARCHAR(30) NOT NULL,
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16) NOT NULL,
          DoB DATE,
          Age INTEGER CHECK(Age>=0),
          Unit VARCHAR(30),
          profilepic PATH,
          FOREIGN KEY (user_id) REFERENCES users(user_id)
          )
          """)

# Appointment Tables

c.execute("""CREATE TABLE IF NOT EXISTS Appointments(
          appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
          slot_tempo DATETIME,
          doctor INTEGER,
          patient INTEGER,
          visit_type INTEGER,
          dispo INTEGER DEFAULT '1',
          quest INTEGER DEFAULT '0',
          FOREIGN KEY (doctor) REFERENCES Doctors(user_id),
          FOREIGN KEY (patient) REFERENCES Patients(user_id), 
          FOREIGN KEY (visit_type) REFERENCES Visits(visit_code)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Visits(
          visit_code INTEGER PRIMARY KEY AUTOINCREMENT,
          Visit VARCHAR(25),
          specialty varchar,
          Unit VARCHAR(30)
          )
          """)

# Report and Prescriptions Tables

c.execute("""CREATE TABLE IF NOT EXISTS VisitReport(
          appointment_id INTEGER PRIMARY KEY,
          file_path path,
          created_at datetime,
          doctor integer,
          patient integer,
          FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id),
          FOREIGN KEY (doctor) REFERENCES Doctors(user_id),
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Prescription(
          prescription_id integer PRIMARY KEY AUTOINCREMENT,
          appointment_id INTEGER,
          patient integer, 
          doctor integer,
          file_path path,
          created_at datetime,
          type varchar,
          FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id),
          FOREIGN KEY (doctor) REFERENCES Doctors(user_id),
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
          )
          """)
    #type is medicine, visit, sensor

# Therapy 

c.execute("""CREATE TABLE IF NOT EXISTS Drugs(
          drug_id integer PRIMARY KEY AUTOINCREMENT,
          name varchar,
          brand_name varchar
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS PrescriptionDrugs(
          prescription_id integer primary key,
          drug1 integer,
          notes text, 
          FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id),
          FOREIGN KEY (drug1) REFERENCES Drugs(drug_id)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Therapy(
          therapy_id integer primary key AUTOINCREMENT, 
          patient integer,
          drug1 integer,
          drug2 integer,
          drug3 integer,
          dosage text, 
          duration integer,
          notes text,
          FOREIGN KEY (drug1) REFERENCES Drugs(drug_id),
          FOREIGN KEY (drug2) REFERENCES Drugs(drug_id),
          FOREIGN KEY (drug3) REFERENCES Drugs(drug_id)
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
          )
          """)
# I put drug because prescriptions can expire and need to be remade
# Duration in days


# Sensors' Tab

c.execute("""CREATE TABLE IF NOT EXISTS PrescriptionDevices(
          prescription_id integer PRIMARY KEY,
          sensor_type varchar, 
          notes text, 
          patient integer,
          FOREIGN KEY (patient) REFERENCES Patients(user_id),
          FOREIGN KEY (prescription_id) REFERENCES Prescription(prescription_id)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Sensors(
          Code_device INTEGER PRIMARY KEY AUTOINCREMENT,
          Name VARCHAR(15) NOT NULL,
          Signal_Acquired VARCHAR(15) NOT NULL,
          availability CHAR(1) CHECK(availability IN('U','A','M')) DEFAULT 'A',
          model TEXT, 
          description text,
          Status TEXT,
          assigned_at_time DATETIME,
          patient integer,
          PrescriptionDevices_id integer,
          warehouse TEXT,
          location TEXT,
          FOREIGN KEY (PrescriptionDevices_id) REFERENCES PrescriptionDevices(PrescriptionDevices_id),
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
          )
          """)


c.execute("""CREATE TABLE IF NOT EXISTS Sessions(
          session_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          Code_device INTEGER NOT NULL,
          Code_device2 INTEGER NOT NULL,
          Code_device3 INTEGER NOT NULL,
          patient integer,
          t_acquisition DATETIME NOT NULL,
          FOREIGN KEY (Code_device) REFERENCES Sensors(Code_device),          
          FOREIGN KEY (Code_device2) REFERENCES Sensors(Code_device),          
          FOREIGN KEY (Code_device3) REFERENCES Sensors(Code_device),          
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
            )
          """)
# Maybe not useful: from the session_id inside the report I can get all the 
# aquisitions

c.execute("""CREATE TABLE IF NOT EXISTS Acquisitions(
          Code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          Code_device INTEGER NOT NULL,
          session_id integer,
          patient integer,
          Signal_acquired CHAR(3) CHECK(Signal_acquired IN('ECG','EMG','EEG')) NOT NULL,
          raw_data PATH,
          t_acquisition DATETIME NOT NULL,
          Amplitude DECIMAL NOT NULL,
          FOREIGN KEY (Code_device) REFERENCES Sensors(Code_device),          
          FOREIGN KEY (patient) REFERENCES Patients(user_id),
          FOREIGN KEY (session_id) REFERENCES Sessions(session_id)         
            )
          """)
#come posso rendere prmary key il tempo di acquisizione e il codice device? rendo superfluo il codice acquisizione
#durata acquisizione? 

c.execute("""CREATE TABLE IF NOT EXISTS Indexes(
          patient INTEGER NOT NULL,
          Code_device INTEGER,
          t_acquisition DATETIME,
          Peak_value DECIMAL,
          Latency DECIMAL,
          session_id integer,
          FOREIGN KEY (patient) REFERENCES Patients(user_id),          
          FOREIGN KEY (session_id) REFERENCES Sessions(session_id),          
          FOREIGN KEY (Code_device) REFERENCES Sensors(Code_device)  
          )        
          """)
#Latency rispetto a picco precedente, se poi servono altri tipi di indicatori potremo aggiungerne
#Status: U=unavailable, A=available, M=maintnence

c.execute("""CREATE TABLE IF NOT EXISTS SensorsReport(
          snreport_id integer primary key AUTOINCREMENT,
          patient integer,  
          report_type varchar,
          file_path path,
          created_at DATETIME,
          session_id integer,
          session2_id integer,
          session3_id integer,          
          FOREIGN KEY (patient) REFERENCES Patients(user_id),
          FOREIGN KEY (session_id) REFERENCES Sessions(session_id), 
          FOREIGN KEY (session2_id) REFERENCES Sessions(session_id),          
          FOREIGN KEY (session3_id) REFERENCES Sessions(session_id)
          )
          """)
# I could have multiple possible sessions and sensors per report 
# The id links to a session table with all the considered sessions
# Each session is linked to different sensors, sessions+sensors are linked to the acquisition

# Questionnaire and Diary for patient

c.execute("""
    CREATE TABLE IF NOT EXISTS SensorQuestionnaire (
        squest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient INTEGER,
        sensor_id INTEGER, 
        session_id INTEGER,
        date DATETIME, 
        created_at DATETIME,
        malfunction TEXT,
        FOREIGN KEY (patient) REFERENCES Patients(user_id),
        FOREIGN KEY (sensor_id) REFERENCES Sensors(Code_device),
        FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
    )
    """)
# SATISFACTION? 
# We could add a satisfaction questionnaire on the usage of the sensors


c.execute("""CREATE TABLE IF NOT EXISTS VisitQuestionnaire(
          vquest_id integer primary key AUTOINCREMENT,
          appointment_id integer,
          pathologies text,
          medication text, 
          physicalactivity text, 
          sleephours text, 
          sleepquality text, 
          diet text, 
          tobacco text, 
          alcohol text, 
          stress text,
          notes text, 
          created_at DATETIME,
          FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
          )
          """)
# Questionnaires should be differentiated for different type of visits

c.execute("""CREATE TABLE PeriodicQuestionnaire (
                questionnaire_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                date DATE NOT NULL,
                sleep_duration INTEGER,
                sleep_quality INTEGER,
                trouble_falling_asleep INTEGER, 
                sleep_disruption INTEGER,
                daytime_sleepiness INTEGER, 
                sleep_hygene INTEGER, 
                stress_level INTEGER,
                sensor_satifaction INTEGER,
                FOREIGN KEY (patient_id) REFERENCES Patients(user_id)
            )
          """)

c.execute("""
            CREATE TABLE QuestionDefinitions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT NOT NULL UNIQUE,
                question_text TEXT NOT NULL,
                option_1 TEXT NOT NULL,
                option_2 TEXT NOT NULL,
                option_3 TEXT NOT NULL,
                option_4 TEXT NOT NULL,
                option_5 TEXT NOT NULL
            )
        """)

# c.execute("""CREATE TABLE IF NOT EXISTS PatientDiary(
#           entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
#           patient INT,
#           sensor_id INT, 
#           session_id INT,
#           start_time TIME,
#           end_time TIME,
#           notes TEXT,
#           created_at DATETIME,
#           malfunction varchar,
#           FOREIGN KEY (patient) REFERENCES Patients(user_id),
#           FOREIGN KEY (sensor_id) REFERENCES Sensors(session_id),
#           FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
#           )
#           """)


#confermo cambiamenti effettuati
connection.commit()
#chiudo connessione al database
connection.close()

# CHECK(role IN('P', 'D', 'T') DEFAULT 'P')