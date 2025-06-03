import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()


# === 3. Add Sensor Prescription During second appointment ===
c.execute("""
    INSERT INTO Prescription (patient, doctor, created_at, type)
    VALUES (?, ?, datetime('now'), ?)
""", (9, 1, 'device'))

sensor_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDevices (prescription_id, sensor_type, notes, patient)
    VALUES (?, ?, ?, ?)
""", (sensor_prescription_id, 'EEG', 'EEG monitoring for', 9))

connection.commit()
connection.close()