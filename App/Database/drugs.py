import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()

# Insert drugs (used in sleep medicine)
# Dopamine agonists (common for RLS/PLMD)
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Pramipexole", "Mirapex"))
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Ropinirole", "Requip"))
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Rotigotine", "Neupro Patch"))

# Anti-seizure medications (alternative for RLS, especially with pain)
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Gabapentin", "Neurontin"))
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Pregabalin", "Lyrica"))

# Iron supplements (low iron linked with RLS)
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Ferrous sulfate", "Iron Supplement"))

# Benzodiazepines (sometimes used for REM Behavior Disorder)
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Clonazepam", "Klonopin"))

# Melatonin (often used for REM Behavior Disorder)
c.execute("INSERT INTO Drugs (name, brand_name) VALUES (?, ?)", ("Melatonin", "Circadin"))


c.execute("""
    INSERT INTO Therapy(patient, drug1, dosage, duration, notes)
    VALUES (?, ?, ?, ?, ?)
""", (4, 9, '0.125 mg at bedtime', 30, 'Start with low-dose Pramipexole for RLS. Titrate if needed.'))

c.execute("""
    INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
    VALUES (?, ?, ?, ?, datetime('now'), ?)
""", (4, 1, 2, 'files/pramipexole_rx.pdf', 'medicine'))

prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDrugs (prescription_id, drug1, notes)
    VALUES (?, ?, ?)
""", (prescription_id, 9, 'Pramipexole 0.125 mg at bedtime for 30 days. Titrate if symptoms persist.'))


connection.commit()
connection.close()
