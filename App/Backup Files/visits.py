import sqlite3
#import pandas as pd
connection=sqlite3.connect('App/Database/gui_database.db')
c=connection.cursor()

c.execute("""
    INSERT INTO Visits(Visit)
    VALUES (?)
""", ('Sleep Check: First Visit',))

c.execute("""
    INSERT INTO Visits(Visit)
    VALUES (?)
""", ('Sleep Check: Follow Up',))

connection.commit()
connection.close()