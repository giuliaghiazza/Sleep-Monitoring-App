import sqlite3

conn = sqlite3.connect("App/Database/gui_database.db")
cursor = conn.cursor()

cursor.execute("""DELETE FROM QuestionDefinitions;""")
cursor.execute("""DELETE FROM PeriodicQuestionnaire;""")
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

cursor.executemany("""
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
    cursor.execute("""
        INSERT INTO PeriodicQuestionnaire (
            patient_id, date, sleep_duration, sleep_quality, trouble_falling_asleep, sleep_disruption, daytime_sleepiness, sleep_hygene, stress_level, sensor_satifaction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (8, date, sd, sq, tfa, sdi, ds, sh, sl, ss))


conn.commit()
conn.close()
