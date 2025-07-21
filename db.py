# db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345',
        database='breast_cancer_patients'
    )

def insert_patient(data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO breast_cancer_patients 
            (patient_name, surname, age, gender, address, mobile_number, date_of_consultation, referring_physician)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['Name'],
            data['surname'],
            data['Age'],
            data['Gender'],
            data['Address'],
            data['Mobile Number'],
            data['Date of consultant'],
            data['Referring Physician']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data inserted successfully.")
    except Exception as e:
        print("❌ Error inserting data:", e)
        
def fetch_all_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM breast_cancer_patients")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
