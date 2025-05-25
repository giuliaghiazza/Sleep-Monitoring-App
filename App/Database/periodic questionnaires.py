import sqlite3

conn = sqlite3.connect("App/Database/gui_database.db")
cursor = conn.cursor()

cursor.execute("""DELETE FROM QuestionDefinitions;""")

questions = [
    ("sleep_duration", "How many hours did you sleep last night?",
     "Less than 4 hours", "4 or 5 hours", "6 hours", "7 or 8 hours", "More than 8 hours"),

    ("sleep_quality", "How would you rate your sleep quality?",
     "Very poor", "Poor", "Average", "Good", "Excellent"),

    ("trouble_falling_asleep", "Did you have trouble falling asleep?",
     "Very poor", "Poor", "Normal", "Good", "Very good"),

    ("sleep_disruption", "Did you wake up during the night?",
     "Never", "Just briefly", "1 or 2 times", "Many times", "I couldn't stay asleep"),

    ("daytime_sleepiness", "How tired did you feel today?",
     "Extremely tired", "Tired", "Moderate", "Slightly tired", "Not tired at all"),

    ("sleep_hygene", "Did you follow a good bedtime routine?",
     "Extremely tired", "Tired", "Moderate", "Slightly tired", "Not tired at all"),

    ("stress_level", "What was your stress level today?",
     "Very high", "High", "Moderate", "Low", "Very low")
]

cursor.executemany("""
INSERT INTO QuestionDefinitions 
(field_name, question_text, option_1, option_2, option_3, option_4, option_5)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", questions)


# entries = [
#     ('2024-04-05', 3, 4, 3, 2, 3, 4, 2),
#     ('2024-04-10', 2, 2, 3, 3, 4, 2, 4),
#     ('2024-04-20', 3, 3, 4, 2, 2, 4, 3),
#     ('2024-04-30', 4, 5, 4, 1, 2, 3, 4),
#     ('2024-05-05', 3, 3, 3, 3, 3, 3, 4),
#     ('2024-05-10', 2, 2, 2, 4, 4, 2, 5),
#     ('2024-05-15', 4, 4, 4, 2, 2, 3, 3),
#     ('2024-05-18', 3, 4, 3, 2, 3, 3, 4),
#     ('2024-05-21', 5, 5, 4, 1, 1, 2, 4),
#     ('2024-05-23', 3, 3, 3, 3, 3, 3, 3),
# ]

# for date, sd, sq, tfa, sd, ds, sh, sl in entries:
#     cursor.execute("""
#         INSERT INTO PeriodicQuestionnaire (
#             patient_id, date, sleep_duration, sleep_quality, trouble_falling_asleep, sleep_disruption, daytime_sleepiness, sleep_hygene, stress_level
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (8, date, sd, sq, tfa, sd, ds, sh, sl))


conn.commit()
conn.close()
