import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()

# Sensors Patients
sensors = [
    (1, "BioSTAMP", "EMG", 1, "Working", "U"),
]

for PrescriptionDevices_id, name, Signal_Acquired, patient, Status, availability in sensors:
    c.execute("""
        INSERT INTO Sensors(PrescriptionDevices_id, name, Signal_Acquired, patient, Status, availability)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (PrescriptionDevices_id, name, Signal_Acquired, patient, Status, availability))

# Sensors available or maintenance 
sensors = [
    ("BioSTAMP2", "EMG", "Working", "M"),
    ("BioSTAMP3", "EMG", "Working", "A"),
    ("ZMachine", "EEG", "Working", "A"),
    ("Biosignalsplux", "EOG", "Working", "A"),
    ("SOMNOWatch", "ACT", "Working", "A")
]

for name, Signal_Acquired, Status, availability in sensors:
    c.execute("""
        INSERT INTO Sensors(name, Signal_Acquired, Status, availability)
        VALUES (?, ?, ?, ?)
    """, (name, Signal_Acquired, Status, availability))

connection.commit()
connection.close()



