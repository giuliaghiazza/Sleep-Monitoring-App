import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()


# ===  Add Therapy ===
# c.execute("""
#     INSERT INTO Therapy(patient, drug1, dosage, duration, notes)
#     VALUES (?, ?, ?, ?, ?)
# """, (8, 1, '0.125 mg at bedtime', 30, 'Start with low-dose Pramipexole for PLM. Titrate if needed.'))


# ===  Add Sensor Prescription During second appointment ===
c.execute("""
    INSERT INTO Prescription (patient, doctor, created_at, type)
    VALUES (?, ?, datetime('now'), ?)
""", (9, 1, 'device'))

sensor_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDevices (prescription_id, sensor_type, notes, patient)
    VALUES (?, ?, ?, ?)
""", (sensor_prescription_id, 'EEG', 'EEG monitoring for', 9))


user_id = 8  
profile_pic_path = 'App/patientprofile.png'  

c.execute("""
    UPDATE Patients
    SET profilepic = ?
    WHERE user_id = ?
""", (profile_pic_path, user_id))

user_id = 5  
profile_pic_path = 'App/patientprofile2.png'  

c.execute("""
    UPDATE Patients
    SET profilepic = ?
    WHERE user_id = ?
""", (profile_pic_path, user_id))

connection.commit()
connection.close()