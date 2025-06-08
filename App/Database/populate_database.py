import sqlite3

conn = sqlite3.connect('App/Database/gui_database.db')
c = conn.cursor()

# USERS 
# c.execute("""DELETE FROM Doctors;""")
# c.execute("""DELETE FROM Technicians;""")
# c.execute("""DELETE FROM Users;""")
# c.execute("""DELETE FROM Patients;""")

# List of doctors: (username, password, Name, Surname, Codice_Fiscale)
doctors = [
    ('Gianna', 'Deluca', 'Gianna', 'Deluca', 'GDADLC02R47D969Q'),
    ('MarcoV', 'MarcoVpass', 'Marco', 'Verdi', 'MRCVRD80A01H501Z'),
]

for username, psw, name, surname, codice_fiscale in doctors:
    c.execute("""
        INSERT INTO users (username, psw, role)
        VALUES (?, ?, ?)
    """, (username, psw, 'D'))
    user_id = c.lastrowid
    c.execute("""
        INSERT INTO Doctors (Name, Surname, Codice_Fiscale, user_id)
        VALUES (?, ?, ?, ?)
    """, (name, surname, codice_fiscale, user_id))

# List of Technicians: (username, password, Name, Surname, Codice_Fiscale)
doctors = [
    ('Luca', 'Scotti', 'Luca', 'Scotti', 'LCASCT96R47D969Q'),
    ('Lisa', 'Gialli', 'Lisa', 'Lisa', 'LSAGLL84R47D969Q'),
]

for username, psw, name, surname, codice_fiscale in doctors:
    c.execute("""
        INSERT INTO users (username, psw, role)
        VALUES (?, ?, ?)
    """, (username, psw, 'T'))
    user_id = c.lastrowid
    c.execute("""
        INSERT INTO Technicians (Name, Surname, Codice_Fiscale, user_id)
        VALUES (?, ?, ?, ?)
    """, (name, surname, codice_fiscale, user_id))

# List of patients: (username, password, Name, Surname)
patients = [
    ('Andrea', 'Greco', 'Andrea', 'Greco', 37, "Male", 1, None, "1988-05-15"),
    ('LucaM', 'pass123', 'Luca', 'Marini', 23, "Male", None, None, None),
    ('AnnaS', 'anna2025', 'Anna', 'Santoro', 57, "Female", None, None, None),
    ('MarioR', 'mario456', 'Mario', 'Rossi', 43, "Male", 1, "Periodic Limb Movements Disorder", None),
    ('ElisaT', 'elisa789', 'Elisa', 'Tarantino', 19, "Female", None, None, None),
]

for username, psw, name, surname, age, gender, doctor, diagnosis, dob in patients:
    c.execute("""
        INSERT INTO users (username, psw, role)
        VALUES (?, ?, ?)
    """, (username, psw, 'P'))
    user_id = c.lastrowid
    c.execute("""
        INSERT INTO patients (Name, Surname, user_id, Age, Gender, assigned_doctor, diagnosis, DoB)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, surname, user_id, age, gender, doctor, diagnosis, dob))

# VISITS 
c.execute("""
    INSERT INTO Visits(Visit)
    VALUES (?)
""", ('Sleep Check: First Visit',))

c.execute("""
    INSERT INTO Visits(Visit)
    VALUES (?)
""", ('Sleep Check: Follow Up',))

# Appointments with (slot_tempo, doctor_id, patient_id, visit_type)
appointments = [
    ('2025-04-15 12:30', 1, 8, 1, 0), 
    ('2025-04-30 16:30', 1, 8, 2, 0), 
    ('2025-05-29 08:30', 1, 5, 1, 0),
    ('2025-05-29 16:30', 1, 7, 2, 0),
    ('2025-06-15 10:00', 1, 5, 2, 0),
    ('2025-05-30 09:00', 1, 8, 2, 0),
    ('2025-05-30 17:00', 1, 6, 1, 0),
    ('2025-04-15 12:30', 2, None, 2, 1),
    ('2025-04-30 16:30', 2, None, 2, 1),
    ('2025-05-29 08:30', 2, None, 2, 1),
    ('2025-05-29 16:30', 2, None, 2, 1),
    ('2025-06-15 10:00', 2, None, 2, 1),
    ('2025-05-30 09:00', 2, None, 2, 1),
    ('2025-06-30 17:00', 1, None, 2, 1),
]

for slot_tempo, doctor_id, patient_id, visit_type, disp in appointments:
    c.execute("""
        INSERT INTO Appointments(slot_tempo, doctor, patient, visit_type, dispo)
        VALUES (?, ?, ?, ?, ?)
    """, (slot_tempo, doctor_id, patient_id, visit_type, disp))


# SENSORS
# Sensors Patients
sensors = [
    (1, "BioSTAMP", "EMG", 8, "Working", "U"),
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


# PERIODIC QUESTIONNAIRE 
questions = [
    ("sleep_duration", "How many hours did you sleep last night?",
     "Less than 4 hours", "4 or 5 hours", "6 hours", "7 or 8 hours", "More than 8 hours"),

    ("sleep_quality", "How would you rate your sleep quality?",
     "Very poor", "Poor", "Average", "Good", "Excellent"),

    ("trouble_falling_asleep", "Did you have trouble falling asleep?",
     "Couldn't fall asleep", "Yes, a bit", "Just sometimes", "Almost never", "No trouble at all"),

    ("sleep_disruption", "Did you wake up during the night?",
     "I couldn't stay asleep", "Many times", "1 or 2 times", "Just briefly", "Never"),

    ("daytime_sleepiness", "How tired did you feel today?",
     "Extremely tired", "Tired", "Moderate", "Slightly tired", "Not tired at all"),

    ("sleep_hygene", "Did you follow a good bedtime routine?",
     "Almost never", "Only a bit", "Sometimes", "Yes, almost everyday", "Always"),

    ("stress_level", "What was your stress level today?",
     "Very high", "High", "Moderate", "Low", "Very low"), 

    ("sensor_satifaction", "How comfortable was using the sensor to sleep?",
     "Very uncomfortable", "A little bit uncomfortable", "Medium", "Comfortable", "Very comfortable")

]

c.executemany("""
INSERT INTO QuestionDefinitions 
(field_name, question_text, option_1, option_2, option_3, option_4, option_5)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", questions)


entries = [
    ('2025-04-05', 2, 2, 2, 2, 2, 2, 2, 3),
    ('2025-04-10', 2, 2, 2, 2, 2, 2, 2, 3),
    ('2025-04-20', 2, 3, 2, 2, 2, 3, 2, 4),
    ('2025-04-30', 3, 2, 3, 3, 3, 3, 2, 5),
    ('2025-05-05', 3, 3, 3, 3, 3, 4, 3, 4),
    ('2025-05-10', 3, 4, 4, 3, 4, 4, 3, 5),
    ('2025-05-15', 4, 4, 4, 4, 4, 3, 4, 5),
    ('2025-05-18', 4, 4, 5, 4, 5, 4, 4, 5),
    ('2025-05-21', 5, 5, 4, 5, 4, 5, 4, 4),
    ('2025-05-23', 5, 5, 5, 5, 5, 5, 5, 5),
]

for date, sd, sq, tfa, sdi, ds, sh, sl, ss in entries:
    c.execute("""
        INSERT INTO PeriodicQuestionnaire (
            patient_id, date, sleep_duration, sleep_quality, trouble_falling_asleep, sleep_disruption, daytime_sleepiness, sleep_hygene, stress_level, sensor_satifaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (8, date, sd, sq, tfa, sdi, ds, sh, sl, ss))


#DRUGS
#Dopamine agonists (common for RLS/PLMD)
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


## FOR PATIENT 8: 
# === 1. Add Therapy ===
c.execute("""
    INSERT INTO Therapy(patient, drug1, dosage, duration, notes)
    VALUES (?, ?, ?, ?, ?)
""", (8, 9, '0.125 mg at bedtime', 30, 'Start with low-dose Pramipexole for RLS. Titrate if needed.'))

# === 2. Add Drug Prescription ===
c.execute("""
    INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
    VALUES (?, ?, ?, ?, datetime('now'), ?)
""", (8, 8, 1, 'Mario Rossi/Reports/Prescriptions/pramipexole_rx.pdf', 'medicine'))

drug_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDrugs (prescription_id, drug1, notes)
    VALUES (?, ?, ?)
""", (drug_prescription_id, 9, 'Pramipexole 0.125 mg at bedtime for 30 days. Titrate if symptoms persist.'))

# === Sensor Prescription During First appointment === 
c.execute("""
    INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
    VALUES (?, ?, ?, ?, datetime('now'), ?)
""", (6, 8, 1, 'Mario Rossi/Reports/Prescriptions/eeg_ZMachine_rx.pdf', 'device'))

sensor_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDevices (prescription_id, sensor_type, notes, patient)
    VALUES (?, ?, ?, ?)
""", (sensor_prescription_id, 'EEG - ZMachine', 'EEG monitoring for diagnosis', 8))

c.execute("""
    INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
    VALUES (?, ?, ?, ?, datetime('now'), ?)
""", (6, 8, 1, 'Mario Rossi/Reports/Prescriptions/emg_biostamp_diag_rx.pdf', 'device'))

sensor_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDevices (prescription_id, sensor_type, notes, patient)
    VALUES (?, ?, ?, ?)
""", (sensor_prescription_id, 'EMG - BioSTAMP', 'EMG monitoring for diagnosis', 8))

# === 3. Add Sensor Prescription During second appointment ===
c.execute("""
    INSERT INTO Prescription (appointment_id, patient, doctor, file_path, created_at, type)
    VALUES (?, ?, ?, ?, datetime('now'), ?)
""", (7, 8, 1, 'Mario Rossi/Reports/Prescriptions/emg_biostamp_rx.pdf', 'device'))

sensor_prescription_id = c.lastrowid

c.execute("""
    INSERT INTO PrescriptionDevices (prescription_id, sensor_type, notes, patient)
    VALUES (?, ?, ?, ?)
""", (sensor_prescription_id, 'EMG - BioSTAMP', 'EMG monitoring for limb movement analysis', 8))

# == Add sensors report === 


# Second visit (report completo)
c.execute("""
    INSERT INTO SensorsReport (patient, file_path, created_at)
    VALUES (?, ?, ?)
""", (8, 'Mario Rossi/Reports/SensorsReports/complete_report.pdf', '2025-04-29 12:30'))

# Third visit 
c.execute("""
    INSERT INTO SensorsReport (patient, file_path, created_at)
    VALUES (?, ?, ?)
""", (8, 'Mario Rossi/Reports/SensorsReports/movement_report.pdf', '2025-05-29 12:30'))

# === 4. Add Visit Report ===
c.execute("""
    INSERT INTO VisitReport (appointment_id, file_path, created_at, doctor, patient)
    VALUES (?, ?, ?, ?, ?)
""", (6, 'Mario Rossi/Reports/VisitReports/visit_2025_04_15.pdf', "2025-04-15", 1, 8)) ## Here first visit
c.execute("""
    INSERT INTO VisitReport (appointment_id, file_path, created_at, doctor, patient)
    VALUES (?, ?, ?, ?, ?)
""", (7, 'Mario Rossi/Reports/VisitReports/visit_2025_04_30.pdf', "2025-04-30", 1, 8)) ## Here second one

# Commit changes
conn.commit()
conn.close()
