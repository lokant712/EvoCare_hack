import sqlite3

conn = sqlite3.connect('evocare.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM patient_access_grants WHERE user_id=1 AND patient_code='P002'")
conn.commit()
print("Cleaned up unwanted grants successfully!")
conn.close()

