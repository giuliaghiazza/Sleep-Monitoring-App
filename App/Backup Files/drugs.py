import sqlite3

connection = sqlite3.connect('App/Database/gui_database.db')
c = connection.cursor()
#Insert drugs (used in sleep medicine)
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


connection.commit()
connection.close()
