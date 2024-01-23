import sqlite3  
  
con = sqlite3.connect("clgdb.db")  
# print("Database opened successfully")  
  

con.execute("create table student (stud_id INTEGER PRIMARY KEY AUTOINCREMENT, Name text, Email text, Address text, Phone integer)")
con.execute("create table teacher (teach_id INTEGER PRIMARY KEY AUTOINCREMENT, Name text, Email text, Address text, Phone integer)")
con.execute("create table login (log_id INTEGER PRIMARY KEY AUTOINCREMENT, username text, password text, is_staff BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT FALSE, is_superuser BOOLEAN DEFAULT FALSE, student_id INT,teacher_id INT,FOREIGN KEY (student_id) REFERENCES student(stud_id),FOREIGN KEY (teacher_id) REFERENCES teacher(teach_id))")

print("Table created successfully")

con=sqlite3.connect('clgdb.db')
cursor = con.cursor()  
cursor.execute("INSERT into login (username, password,is_superuser) values ('admin','admin',True)")  
con.commit()  

