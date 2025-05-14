import sqlite3
#import pandas as pd
connection=sqlite3.connect('gui_database.db')
c=connection.cursor()
c.execute("""DROP TABLE patients;""")

c.execute("""CREATE TABLE IF NOT EXISTS patients(
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          Name VARCHAR(30),
          Codice_Fiscale CHAR(16),
          DoB DATE,
          Age INTEGER CHECK(Age>=0),
          City_of_Birth VARCHAR(20),
          Province_of_Birth CHAR(2),
          City_of_Recidency VARCHAR(20),
          Province_of_Recidency CHAR(2),
          CAP INTEGER,
          nome_utente VARCHAR(30) NOT NULL,
          psw VARCHAR(30) NOT NULL, 
          role VARCHAR(10)  )
          """)

c.execute("""CREATE TABLE IF NOT EXISTS Doctors(
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          Name VARCHAR(30) NOT NULL,
          Codice_Fiscale CHAR(16) NOT NULL,
          DoB DATE NOT NULL,
          Age INTEGER CHECK(Age>=0) NOT NULL,
          Unit VARCHAR(30))
          """)
#Unit: in which he works in the hospital

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

c.execute("""INSERT INTO patients(nome_utente, psw, role)
          VALUES ('Pippo','Franco', 'P')
          """)

#confermo cambiamenti effettuati
connection.commit()
#chiudo connessione al database
connection.close()

# CHECK(role IN('P', 'D', 'T') DEFAULT 'P')