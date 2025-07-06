# create_db.py
import sqlite3

# Connect to the SQLite database (this will create the file if it doesn't exist)
conn = sqlite3.connect('zus_outlets.db')
cursor = conn.cursor()

# Create the outlets table
# We are creating a simple schema with name, address, and opening hours.
cursor.execute('''
CREATE TABLE IF NOT EXISTS outlets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    opening_hours TEXT
);
''')

# Clear existing data to avoid duplicates when re-running the script
cursor.execute("DELETE FROM outlets;")

# Sample data based on ZUS Coffee's website
outlets_data = [
    ('ZUS Coffee - The Curve', 'Lot GZF-1, Ground Floor, The Curve, Mutiara Damansara, 47810 Petaling Jaya, Selangor', '8:00 AM - 10:00 PM'),
    ('ZUS Coffee - Bangsar Shopping Centre', 'Lot F-1, 1st Floor, Bangsar Shopping Centre, 285, Jalan Maarof, 59000 Kuala Lumpur', '9:00 AM - 9:00 PM'),
    ('ZUS Coffee - Pavilion KL', 'P1.11.00, Level 1, Pavilion KL, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur', '10:00 AM - 10:00 PM'),
    ('ZUS Coffee - Sunway Pyramid', 'LG2.69, Lower Ground 2, Sunway Pyramid, 3, Jalan PJS 11/15, Bandar Sunway, 47500 Petaling Jaya', '10:00 AM - 10:00 PM'),
    ('ZUS Coffee - Mid Valley Megamall', 'LG-076, Lower Ground Floor, Mid Valley Megamall, Lingkaran Syed Putra, 59200 Kuala Lumpur', '10:00 AM - 10:00 PM')
]

# Insert the data into the table
cursor.executemany('INSERT INTO outlets (name, address, opening_hours) VALUES (?, ?, ?)', outlets_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'zus_outlets.db' created and populated successfully.")
