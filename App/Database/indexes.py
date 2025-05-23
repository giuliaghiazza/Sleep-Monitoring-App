
import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()
c.execute("""DROP TABLE IF EXISTS Indexes""")

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

#confermo cambiamenti effettuati
connection.commit()
#chiudo connessione al database
connection.close()