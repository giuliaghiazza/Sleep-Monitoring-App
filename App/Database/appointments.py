import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()

c.execute("""DELETE FROM Appointments;""")

# Appointments with (slot_tempo, doctor_id, patient_id, visit_type)
appointments = [
    ('2025-04-15 12:30', 1, 8, 1), 
    ('2025-04-30 16:30', 1, 8, 2), 
    ('2025-05-29 08:30', 1, 5, 1),
    ('2025-05-29 16:30', 1, 7, 2),
    ('2025-06-15 10:00', 1, 5, 2),
    ('2025-05-30 09:00', 1, 8, 2),
    ('2025-05-30 17:00', 1, 6, 1),
]

for slot_tempo, doctor_id, patient_id, visit_type in appointments:
    c.execute("""
        INSERT INTO Appointments(slot_tempo, doctor, patient, visit_type)
        VALUES (?, ?, ?, ?)
    """, (slot_tempo, doctor_id, patient_id, visit_type))

connection.commit()
connection.close()
