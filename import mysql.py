import mysql.connector
import datetime
import cv2
from pyzbar.pyzbar import decode

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jaiforjai18",  # Replace with your actual MySQL password
        database="food_tracker"
    )

def create_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            barcode VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            expiry_date DATE
        )
    """)
    db.commit()
    db.close()

def add_food_item(barcode, name, expiry_date):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO food_items (barcode, name, expiry_date) 
        VALUES (%s, %s, %s) 
        ON DUPLICATE KEY UPDATE name=%s, expiry_date=%s
    """, (barcode, name, expiry_date, name, expiry_date))
    db.commit()
    db.close()

def scan_barcode():
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        barcodes = decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            print(f"Scanned Barcode: {barcode_data}")
            cap.release()
            cv2.destroyAllWindows()
            return barcode_data
        cv2.imshow("Barcode Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return None

def check_expiry_notifications():
    db = connect_db()
    cursor = db.cursor()
    today = datetime.date.today()
    alert_date = today + datetime.timedelta(days=15)
    cursor.execute("SELECT name, expiry_date FROM food_items WHERE expiry_date <= %s", (alert_date,))
    items = cursor.fetchall()
    db.close()
    if items:
        print("Products nearing expiry:")
        for item in items:
            print(f"- {item[0]} (Expires on {item[1]})")
    else:
        print("No products nearing expiry.")

def main():
    create_table()
    while True:
        print("\n1. Scan Product Barcode")
        print("2. Check Expiry Notifications")
        print("3. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            barcode = scan_barcode()
            if barcode:
                name = input("Enter product name: ")
                expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
                add_food_item(barcode, name, expiry_date)
                print("Product added successfully!")
        elif choice == '2':
            check_expiry_notifications()
        elif choice == '3':
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
