import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()
c.execute("""DROP TABLE Users;""")
c.execute("""DROP TABLE Patients;""")
c.execute("""DROP TABLE Doctors;""")
c.execute("""DROP TABLE Technicians;""")
c.execute("""DROP TABLE Appointments;""")

c.execute("""CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    psw VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL
    )"""     
    )

c.execute("""CREATE TABLE IF NOT EXISTS Patients(
          user_id INTEGER PRIMARY KEY,          
          Name VARCHAR(30),
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16),
          DoB DATE,
          Age INTEGER CHECK(Age>=0),
          City_of_Birth VARCHAR(20),
          Province_of_Birth CHAR(2),
          City_of_Recidency VARCHAR(20),
          Province_of_Recidency CHAR(2),
          CAP INTEGER,
          FOREIGN KEY (user_id) REFERENCES users(user_id)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Doctors(
          user_id INTEGER PRIMARY KEY,
          Name VARCHAR(30) NOT NULL,
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16) NOT NULL,
          DoB DATE,
          Age INTEGER CHECK(Age>=0),
          Unit VARCHAR(30),
          FOREIGN KEY (user_id) REFERENCES users(user_id)
          )
          """)
#Unit: in which he works in the hospital

c.execute("""CREATE TABLE IF NOT EXISTS Technicians(
          user_id INTEGER PRIMARY KEY,
          Name VARCHAR(30) NOT NULL,
          Surname VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16) NOT NULL,
          DoB DATE,
          Age INTEGER CHECK(Age>=0),
          Unit VARCHAR(30),
          FOREIGN KEY (user_id) REFERENCES users(user_id)
          )
          """)


c.execute("""CREATE TABLE IF NOT EXISTS Appointments(
          appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
          slot_tempo DATETIME,
          doctor INTEGER,
          patient INTEGER,
          visit_type INTEGER,
          FOREIGN KEY (doctor) REFERENCES Doctors(user_id),
          FOREIGN KEY (patient) REFERENCES Patients(user_id)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Visits(
          visit_code INTEGER PRIMARY KEY AUTOINCREMENT,
          Visit VARCHAR(25),
          Unit VARCHAR(30)
          )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Sensors(
          Code INTEGER PRIMARY KEY AUTOINCREMENT,
          Name VARCHAR(15) NOT NULL,
          Signal_Acquired VARCHAR(15) NOT NULL,
          Status CHAR(1) CHECK(Status IN('U','A','M')) DEFAULT 'A')
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Acquisitions(
          Code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          Code_device INTEGER NOT NULL,
          Signal_acquired CHAR(3) CHECK(Signal_acquired IN('ECG','EMG','EEG')) NOT NULL,
          t_acquisition DATETIME NOT NULL,
          Amplitude DECIMAL NOT NULL)
          """)
#come posso rendere prmary key il tempo di acquisizione e il codice device? rendo superfluo il codice acquisizione

c.execute("""CREATE TABLE IF NOT EXISTS Indexes(
          Code_device INTEGER NOT NULL,
          t_acquisition DATETIME NOT NULL,
          Peak_value DECIMAL NOT NULL,
          Latency DECIMAL NOT NULL)
          """)
#Latency rispetto a picco precedente, se poi servono altri tipi di indicatori potremo aggiungerne
#Status: U=unavailable, A=available, M=maintnence

#confermo cambiamenti effettuati
connection.commit()
#chiudo connessione al database
connection.close()

# CHECK(role IN('P', 'D', 'T') DEFAULT 'P')