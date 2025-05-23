import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()

# c.execute("""DELETE FROM Doctors;""")
# c.execute("""DELETE FROM Technicians;""")
# c.execute("""DELETE FROM Users;""")
# c.execute("""DELETE FROM Patients;""")

# List of doctors: (username, password, Name, Surname, Codice_Fiscale)
doctors = [
    ('Gianna', 'Bianchi', 'Gianna', 'Bianchi', 'GHZGLI02R47D969Q'),
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
    ('Luca', 'Gialli', 'Luca', 'Gialli', 'LCAGLL96R47D969Q'),
    ('Lisa', 'Scotti', 'Lisa', 'Lisa', 'LSASCT84R47D969Q'),
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
    ('Pippo', 'Franco', 'Pippo', 'Rossi', 37, "Male", 1, None),
    ('LucaM', 'pass123', 'Luca', 'Marini', 23, "Male", None, None),
    ('AnnaS', 'anna2025', 'Anna', 'Santoro', 57, "Female", None, None),
    ('MarioR', 'mario456', 'Mario', 'Rossi', 43, "Male", 1, "Periodic Limb Movements Disorder"),
    ('ElisaT', 'elisa789', 'Elisa', 'Tarantino', 19, "Female", None, None),
]

for username, psw, name, surname, age, gender, doctor, diagnosis in patients:
    c.execute("""
        INSERT INTO users (username, psw, role)
        VALUES (?, ?, ?)
    """, (username, psw, 'P'))
    user_id = c.lastrowid
    c.execute("""
        INSERT INTO patients (Name, Surname, user_id, Age, Gender, assigned_doctor, diagnosis)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, surname, user_id, age, gender, doctor, diagnosis))

connection.commit()
connection.close()