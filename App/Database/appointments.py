import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()

# Appointments with (slot_tempo, doctor_id, patient_id, visit_type)
appointments = [
    ('2025-05-17 08:30', 6, 1, 1),
    ('2025-05-17 10:00', 6, 2, 2),
    ('2025-05-17 11:30', 7, 3, 1),
    ('2025-05-17 14:00', 7, 4, 2),
    ('2025-05-18 09:00', 6, 5, 1),
    ('2025-05-18 15:30', 7, 1, 2),
    ('2025-05-18 17:00', 6, 3, 1),
]

for slot_tempo, doctor_id, patient_id, visit_type in appointments:
    c.execute("""
        INSERT INTO Appointments(slot_tempo, doctor, patient, visit_type)
        VALUES (?, ?, ?, ?)
    """, (slot_tempo, doctor_id, patient_id, visit_type))

connection.commit()
connection.close()
