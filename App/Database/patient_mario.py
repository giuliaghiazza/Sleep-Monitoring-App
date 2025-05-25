import sqlite3

conn = sqlite3.connect('App/Database/gui_database.db')
c = conn.cursor()

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
    VALUES (?, ?, datetime('now'), ?, ?)
""", (6, 'Mario Rossi/Reports/VisitReports/visit_2024_04_15.pdf', 1, 8)) ## Here first visit
c.execute("""
    INSERT INTO VisitReport (appointment_id, file_path, created_at, doctor, patient)
    VALUES (?, ?, datetime('now'), ?, ?)
""", (7, 'Mario Rossi/Reports/VisitReports/visit_2024_04_30.pdf', 1, 8)) ## Here second one

# === Sensor Performance === 
c.execute("""
    INSERT INTO SensorsPerformanceReport (patient, file_path, created_at, code_device)
    VALUES (?, ?, ?, ?)
""", (8, 'Mario Rossi/Reports/PerformanceReport/complete_report.pdf', '2025-05-29 12:30', 1))

# Commit changes
conn.commit()
conn.close()
