from flask import *
import sqlite3  

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/stud_reg', methods=['GET', 'POST'])
def reg_stud():
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        un = request.form['username']
        pwd = request.form['pwd']
        address = request.form['address']
        phone = request.form['phone']

        con = sqlite3.connect('clgdb.db')
        cursor = con.cursor()

        # Insert into student table
        cursor.execute("INSERT INTO student (Name, Email, Address, Phone) VALUES (?, ?, ?, ?)", (name, mail, address, phone))
        con.commit()

        # Get the student_id of the newly inserted student
        student_id = cursor.lastrowid

        # Insert into login table with foreign key reference to student
        cursor.execute("INSERT INTO login (username, password, is_staff, is_active, student_id, teacher_id) VALUES (?, ?, ?, ?, ?, ?)",
                       (un, pwd, False, False, student_id, None))  # Assuming teacher_id is not applicable for students
        con.commit()
        return redirect(url_for('home'))
    else:
        return render_template('stud_reg.html')

def authenticate(username, password):
    con = sqlite3.connect('clgdb.db')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM login WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    return user

@app.route('/login', methods=['GET', 'POST'])
def loging():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       user = authenticate(username, password)
       if user is not None and user[5] == 1:  # Assuming is_superuser is the sixth column
            return redirect(url_for('admin_home'))
       elif user is not None and user[3] == 1:  
           session['user_id'] = user[0]
           return redirect(url_for('teacher_profile'))
       elif user is not None and user[4] == 1:  
           session['user_id'] = user[0]
           return redirect(url_for('stud_profile')) 
       else:
        return redirect(url_for('loginfail'))
           
    else:
        return render_template('login.html')
    
@app.route('/loginfail')
def loginfail():
    return render_template('loginfail.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from the session
    return redirect(url_for('loging'))

    

# admin module
@app.route('/adminhome')
def admin_home():
    con = sqlite3.connect("clgdb.db")    
    cursor = con.cursor() 
    cursor.execute('SELECT COUNT(*) FROM teacher')
    teacher_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.is_active = True')
    stud_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.is_active = False')
    stud_count_false = cursor.fetchone()[0]
    return render_template('adminhome.html',teacher_count=teacher_count, stud_count=stud_count, stud_count_false=stud_count_false)

@app.route('/admin_teacher')
def adminteacher():
    return render_template('admin_teacher.html')

@app.route('/teacher_reg', methods=['GET', 'POST'])
def addteacher():
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        un = request.form['username']
        pwd = request.form['pwd']
        address = request.form['address']
        phone = request.form['phone']

        con = sqlite3.connect('clgdb.db')
        cursor = con.cursor()

        # Insert into student table
        cursor.execute("INSERT INTO teacher (Name, Email, Address, Phone) VALUES (?, ?, ?, ?)", (name, mail, address, phone))
        con.commit()

        teacher_id = cursor.lastrowid

        cursor.execute("INSERT INTO login (username, password, is_staff, is_active, student_id, teacher_id) VALUES (?, ?, ?, ?, ?, ?)",
                       (un, pwd, True, True, None, teacher_id)) 
        con.commit()
        return redirect(url_for('viewteacher'))
    else:
        return render_template('teacher_reg.html')

@app.route('/admin_view_teacher')
def viewteacher():
    con = sqlite3.connect("clgdb.db")  
    con.row_factory = sqlite3.Row  
    cursor = con.cursor()  
    cursor.execute("select * from teacher")  
    data = cursor.fetchall()  
    return render_template('admin_view_teacher.html', data=data)

@app.route('/admin_delete_teacher/<int:teach_id>')
def deletedata(teach_id):
   con = sqlite3.connect("clgdb.db")    
   cursor = con.cursor() 
   cursor.execute('DELETE FROM login WHERE teacher_id = %d' %teach_id)
   cursor.execute('delete from teacher where teach_id=%d' %teach_id)
   con.commit()
   return redirect(url_for('viewteacher'))

@app.route('/admin_student')
def adminstudent():
    return render_template('admin_student.html')

@app.route('/admin_view_student')
def viewstudent():
    con = sqlite3.connect("clgdb.db")  
    con.row_factory = sqlite3.Row  
    cursor = con.cursor()  
    cursor.execute("SELECT * FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.is_active = True") 
    data = cursor.fetchall()  
    return render_template('admin_view_student.html', data=data)

@app.route('/admin_delete_stud/<int:stud_id>')
def deletedata1(stud_id):
   con = sqlite3.connect("clgdb.db")    
   cursor = con.cursor() 
   cursor.execute('DELETE FROM login WHERE student_id = %d' %stud_id)
   cursor.execute('delete from student where stud_id=%d' %stud_id)
   con.commit()
   return redirect(url_for('viewstudent'))

@app.route('/admin_approve_stud')
def approve():
    con = sqlite3.connect("clgdb.db")  
    con.row_factory = sqlite3.Row  
    cursor = con.cursor()  
    cursor.execute("SELECT * FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.is_active = false")  
    data = cursor.fetchall()  
    return render_template('admin_approve_stud.html', data=data)

@app.route('/confirmstud/<int:stud_id>')
def confirm(stud_id):
    con = sqlite3.connect("clgdb.db")    
    cursor = con.cursor() 
    cursor.execute("update login set is_active = True where student_id=%d" %stud_id)
    con.commit()  
    return redirect(url_for('approve'))

# teacher module

@app.route('/teacher_profile1')
def teacher_profile():
    user_id = session.get('user_id')
    if user_id is not None:
        con = sqlite3.connect("clgdb.db")    
        cursor = con.cursor() 
        cursor.execute('SELECT * FROM teacher LEFT JOIN login ON teacher.teach_id = login.teacher_id WHERE login.log_id=%d'%user_id)
        teacher_data = cursor.fetchone()
        return render_template('teacher_profile.html', teacher_data=teacher_data)
    else:
        return redirect(url_for('login'))

@app.route('/teacher_edit/<int:teach_id>', methods=['POST', 'GET'])
def editteacher(teach_id): 
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        address = request.form['address']
        phone = request.form['phone']

        con = sqlite3.connect('clgdb.db')
        cursor = con.cursor() 
        cursor.execute("update teacher set Name=?, Email=?, Address=?, Phone=? where teach_id=?",(name,mail,address,phone,teach_id))  
        con.commit()  
        return redirect(url_for('teacher_profile'))
    else:  
        con = sqlite3.connect("clgdb.db")  
        con.row_factory = sqlite3.Row  
        cursor = con.cursor()  
        cursor.execute('SELECT * FROM teacher where teach_id=%d' %teach_id)  
        data = cursor.fetchone()  
        return render_template('teacher_edit.html', data=data)

@app.route('/teacher_stud')
def teacher_viewstudent():
    con = sqlite3.connect("clgdb.db")  
    con.row_factory = sqlite3.Row  
    cursor = con.cursor()  
    cursor.execute("SELECT * FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.is_active = True") 
    data = cursor.fetchall()  
    return render_template('teacher_stud.html', data=data)

# student module
@app.route('/stud_profile1')
def stud_profile():
    user_id = session.get('user_id')
    if user_id is not None:
        con = sqlite3.connect("clgdb.db")    
        cursor = con.cursor() 
        cursor.execute('SELECT * FROM student LEFT JOIN login ON student.stud_id = login.student_id WHERE login.log_id=%d'%user_id)
        stud_data = cursor.fetchone()
        return render_template('stud_profile.html', stud_data=stud_data)
    else:
        return redirect(url_for('login'))

@app.route('/stud_edit/<int:stud_id>', methods=['POST', 'GET'])
def editstudent(stud_id): 
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        address = request.form['address']
        phone = request.form['phone']

        con = sqlite3.connect('clgdb.db')
        cursor = con.cursor() 
        cursor.execute("update student set Name=?, Email=?, Address=?, Phone=? where stud_id=?",(name,mail,address,phone,stud_id))  
        con.commit()  
        return redirect(url_for('stud_profile'))
    else:  
        con = sqlite3.connect("clgdb.db")  
        con.row_factory = sqlite3.Row  
        cursor = con.cursor()  
        cursor.execute('SELECT * FROM student where stud_id=%d' %stud_id)  
        data = cursor.fetchone()  
        return render_template('student_edit.html', data=data)
    
@app.route('/stud_teacher')
def stud_viewteacher():
    con = sqlite3.connect("clgdb.db")  
    con.row_factory = sqlite3.Row  
    cursor = con.cursor()  
    cursor.execute("select * from teacher")  
    data = cursor.fetchall()  
    return render_template('stud_teacher.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
   

# @app.route('/editform/<int:id>', methods=['POST', 'GET'])
# def editdata(id): 
#     if request.method=='POST':
#       name=request.form['fn']
#       age=request.form['age']
#       mail=request.form['mail']
#       con=sqlite3.connect('stud_db.db')
#       cursor = con.cursor()  
#       cursor.execute("update Student set name=?, email=?, age=? where id=?",(name,mail,age,id))  
#       con.commit()  
#       return redirect(url_for('view'))
#     else: 
#         con = sqlite3.connect("stud_db.db")  
#         con.row_factory = sqlite3.Row  
#         cursor = con.cursor()  
#         cursor.execute('select * from Student where id=%d'%id)  
#         data = cursor.fetchone()  
#         return render_template('edit.html', data=data)
    

   