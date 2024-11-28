import sqlite3

# Connect to the SQLite database (adjust the path if necessary)
conn = sqlite3.connect(r'C:\Users\Abdullah Mohammed\PycharmProjects\personal_task_manager\instance\site.db')
cursor = conn.cursor()

# Update the roles in the user table
cursor.execute("UPDATE user SET role = 'User' WHERE role NOT IN ('Admin', 'User')")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Roles updated successfully!")
