import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()

c.execute("""DELETE FROM Therapy;""")


# === 1. Add Therapy ===
c.execute("""
    INSERT INTO Therapy(patient, drug1, dosage, duration, notes)
    VALUES (?, ?, ?, ?, ?)
""", (8, 1, '0.125 mg at bedtime', 30, 'Start with low-dose Pramipexole for RLS. Titrate if needed.'))


connection.commit()
connection.close()