import psycopg2
import functions
from flask import Flask, render_template, request, redirect,session, flash, url_for, send_from_directory, abort 
import io,os
import base64
from itertools import zip_longest
import matplotlib.pyplot as plt
import datetime
from deep_translator import GoogleTranslator


app430 = Flask(__name__)
app430.secret_key = 'rashamalaeb'

#GLOBAL VAR 
app430.config['insert_emp_not_successfull'] = False
app430.config["insert_new_empskill_success"] = True
app430.config["insert_log_hours_success"] = True 
app430.config["insert_task_success"] = True 
app430.config["update_task_success"] = True 
app430.config["insert_project_success"] = True
app430.config["add_emp_success"] = True
app430.config["rating_success"] = True

@app430.route('/')
def home():
    isManager = False
    if 'username' not in session:
        logged_in = False
    else: 
        logged_in=True
        if functions.is_manager(session['username']): isManager = True
    return render_template('home.html', session_logged_in= logged_in, isManager = isManager)


@app430.route('/calendar')
def calendar():
    if functions.is_manager(session['username']):
        return render_template('calendar.html', session_logged_in = True, isManager= True)
    else:
        return render_template('calendar.html', session_logged_in = True, isManager= False)


####################################### USER AUTHENTICATION ##############################################################

#SIGNUP 
@app430.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       functions.signup(username, password)

       flash('Signup successful!', 'success')
       return redirect('/login')

    return render_template('signup.html')

#LOGIN
@app430.route('/login', methods=['GET', 'POST'])
def login():
    login_failed = False 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if functions.authenticate_user(username, password):
            session['username'] = username  
            flash('Login successful!', 'success')
            if functions.is_manager(username):
                return redirect('/employees')
            else:
                return redirect('/employee')
        else:
            flash('Login failed. Please try again.', 'error')
            login_failed = True 
    return render_template('login.html', login_failed = login_failed)

#LOGOUT
@app430.route('/logout')
def logout():
    session.pop('logged_in', None) 
    session.pop('username', None)  
    flash('You have been logged out.', 'info')
    return redirect('/')

########################################################################################################

##############################################TASKS_MANAGER#####################################################
#Tasks Main Route 
@app430.route('/tasks')
def tasks():
    if 'username' not in session:
        return redirect('/')
    elif functions.is_manager(session['username']):
        conn = functions.get_db_connection()
        cursor = conn.cursor()
        ssn= session['username']
        cursor.execute("SELECT *FROM EMPLOYEE_TASK1")
        tasks=cursor.fetchall()
        conn.close()
        return render_template('tasks.html', tasks= tasks, session_logged_in = True, insert_task_success = app430.config["insert_task_success"], update_task_success = app430.config["update_task_success"])
    else:
        conn = functions.get_db_connection()
        cursor = conn.cursor()
        ssn=session['username']
        cursor.execute("SELECT *FROM EMPLOYEE_TASK1 where essn=%s ",(ssn,))
        tasks=cursor.fetchall()
        conn.close()
        return render_template('tasks.html', tasks= tasks, session_logged_in = True, insert_task_success = app430.config["insert_task_success"] , update_task_success = app430.config["update_task_success"])

#Insert Task
@app430.route('/inserttask', methods=['POST'])
def insert_task():
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    tname = request.form['tname']
    essns_input = request.form['essns']
    #essn = request.form['essn']
    deadline = request.form['deadline']
    description = request.form['description']
    total_hours= request.form['total_hours']
    requited_hours=request.form['requited_hours']
    
    essn_parts = [essn.strip() for essn in essns_input.split(',')]
    for essn in essn_parts:
        app430.config["insert_task_success"] = functions.insert_new_task(conn,cursor,tname,essn,deadline,description,total_hours,requited_hours)
    conn.close()
    return redirect ('/tasks')

#DELETE TASK 
@app430.route('/delete_task', methods=['POST'])
def delete_task():
    # Retrieve employee SSN from the request
    tname = request.form.get('tname')
    essn = request.form.get('essn')
    deadline = request.form.get('deadline')

    # Delete the employee from the database based on SSN
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM EMPLOYEE_TASK1 WHERE Tname = %s AND Essn = %s AND Deadline = %s", (tname, essn, deadline))
    conn.commit()
    conn.close()
    return redirect('/tasks')

#UPDATE TASKS WORK HOURS
@app430.route('/update_task_hours', methods=['POST'])
def update():
    if request.method == 'POST':
        # Handle rating submission
        ssn = request.form['ssn']
        tname = request.form['tname']
        total_hours = int(request.form['total_hours'])

        conn = functions.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE EMPLOYEE_TASK1 SET TOTAL_HOURS=%s WHERE Tname ILIKE %s AND essn=%s", (total_hours, tname, ssn))
            conn.commit()
            app430.config["update_task_success"] = functions.check_ssn_exists(ssn)
            # Redirect to a success page or render a template
            return redirect('/tasks')
        except psycopg2.Error as e:
            conn.rollback()
            # Provide an error message to the user
            return "An error occurred while updating task hours.", 500
        finally:
            conn.close()
    else:
        # Render the form template
        return render_template("tasks.html", insert_task_success = app430.config["insert_task_success"] , update_task_success = app430.config["update_task_success"])
    
###############################################################################################################################

################################################EMPLOYEES######################################################################
@app430.route('/employees')
def employees():
    if 'username' not in session:
        return redirect(url_for('login'))
    elif functions.is_manager(session['username']):
        conn = functions.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employee")
        employees = cursor.fetchall()
        cursor.execute("SELECT * FROM EMPLOYEE_SKILLS")
        empskills = cursor.fetchall()
        cursor.execute("SELECT *FROM EMPLOYEE_PROJECT")
        emprojects=cursor.fetchall()
        cursor.execute("SELECT *FROM EMPLOYEE_WORK_LOG")
        employee_workdate= cursor.fetchall()
        conn.close()
        return render_template('indexfinal.html', employees = employees, empskills= empskills, emprojects = emprojects, employee_workdate=employee_workdate, session_logged_in = True, insert_not_successfull = app430.config["insert_emp_not_successfull"], insert_new_empskill_success = app430.config["insert_new_empskill_success"], insert_log_hours_success = app430.config["insert_log_hours_success"], zip=zip)
    else:
        return render_template('home.html', session_logged_in = False)

@app430.route('/insertemployee', methods=['POST'])
def insert_employee():
    conn = functions.get_db_connection()
    
    cursor = conn.cursor()
    ssn = request.form['ssn']
    fname = request.form['fname']
    minit = request.form['minit']
    lname = request.form['lname']
    address = request.form['address']
    sex = request.form['sex']
    salary = request.form['salary']
    super_ssn = request.form['super_ssn']
    dno = request.form['dno']
    attendance = request.form['attendance']
    life_cycle = request.form['life_cycle']
    position = request.form['position']
    app430.config["insert_emp_not_successfull"] =  functions.insert_new_employee(conn, cursor, fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, attendance, life_cycle, position)
    conn.close()

    return redirect('/employees')

@app430.route('/delete_employee', methods=['POST'])
def delete_employee():
    # Retrieve employee SSN from the request
    ssn = request.form.get('ssn')

    # Delete the employee from the database based on SSN
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM EMPLOYEE WHERE Ssn = %s", (ssn,))
    conn.commit()
    conn.close()

    # Redirect the user to the same page after deletion
    return redirect('/employees')


@app430.route('/insertEskills', methods=['POST'] )
def insert_skills():
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    essn= request.form['essn']
    skill=request.form['skill']
    app430.config["insert_new_empskill_success"] = functions.insert_new_empskill(conn,cursor,essn,skill)
    conn.close()
    return redirect ('/employees')

@app430.route('/log_work_hours', methods=['POST'])
def log_work_hours():
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    ssn = request.form['ssn']
    work_date = request.form['work_date']
    total_hours = request.form['total_hours']
    app430.config["insert_log_hours_success"] = functions.insert_workhours(conn,cursor,ssn,work_date,total_hours)
    conn.close()
    return redirect ('/employees')

#################################################################################################################

##############################################PROJECTS###########################################################
@app430.route('/projects')
def projects():
    if 'username' not in session:
        return redirect(url_for('login'))
    elif functions.is_manager(session['username']):
        conn = functions.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EMPLOYEE_SKILLS")
        empskills = cursor.fetchall()
        cursor.execute("SELECT *FROM EMPLOYEE_PROJECT")
        emprojects=cursor.fetchall()
        conn.close()
        return render_template('projects.html', empskills= empskills, emprojects = emprojects, session_logged_in = True,insert_task_success = app430.config["insert_task_success"], add_emp_success = app430.config["add_emp_success"])
    else:
        return render_template('home.html', session_logged_in = False)
    
@app430.route('/matching',methods=['POST'])
def match():
    #conn = functions.get_db_connection()
    
    skills_str = request.form['skills']
    # Split skills string into a list of skills
    skills = [skill.strip() for skill in skills_str.split(',')]
    employees = functions.skill_matching(skills)
    
    return render_template('projects.html', employees = employees, session_logged_in= True, isManager = True)

@app430.route('/insertEprojects', methods=['POST'])
def insert_projects():
    conn = functions.get_db_connection()
    

    pname = request.form['pname']
    pno = int(request.form['pno'])  
    location = request.form['location']
    deadline = datetime.datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() 
    budget = int(request.form['budget']) 
    department = int(request.form['department']) 
    
    skills_str = request.form['skills']
    # Split skills string into a list of skills
    skills = [skill.strip() for skill in skills_str.split(',')]

    val1 = functions.insert_new_emproject(conn,  pname, pno, location, deadline, budget, department)
    val2= functions.insert_project_skills(pno,skills)
    app430.config["insert_project_success"] = val1 and val2; 
    employees = functions.skill_matching(skills)
    
    conn.close()

    return render_template('projects.html',session_logged_in = True, employees = employees , insert_task_success = app430.config["insert_task_success"], add_emp_success = app430.config["add_emp_success"])

@app430.route('/insert_employee_project',methods=['POST'])
def insert_employee_project():
    #conn = functions.get_db_connection()
    pno = request.form['pnum']
    selected = request.form['selected']
    # Split skills string into a list of skills
    ssn_selected_employees = [s.strip() for s in selected.split(',')]
    app430.config["add_emp_success"] = functions.add_employees_to_project(ssn_selected_employees,pno)
    return redirect ('/projects')

################################################################################################################

##############################################EMPLOYEE############################################################
@app430.route('/employee')
def employee():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    ssn=session['username']
    cursor.execute("SELECT * FROM employee where ssn=%s ",(ssn,))
    employees = cursor.fetchall()
    cursor.execute("SELECT *FROM EMPLOYEE_TASK1 where essn=%s ",(ssn,))
    tasks=cursor.fetchall()
    cursor.execute("SELECT * FROM EMPLOYEE_SKILLS where essn=%s ",(ssn,))
    empskills = cursor.fetchall()
    cursor.execute("SELECT *FROM EMPLOYEE_PROJECT where essn=%s ",(ssn,))
    emprojects=cursor.fetchall()
    cursor.execute("SELECT *FROM EMPLOYEE_WORK_LOG where ssn=%s ",(ssn,))
    employee_workdate= cursor.fetchall()
    return render_template('employee.html',employees=employees,tasks=tasks,empskills=empskills,emprojects=emprojects,employee_workdate=employee_workdate,session_logged_in = True, zip=zip)

#################################################################################################################

#######################################PROGRESS AND SUSTAINABILITY###############################################
@app430.route('/progress', methods=['POST'])
def progress():
    super_ssn = session['username']
    connection = functions.get_db_connection()
    if connection:
        functions.delete()
        supervisees, names = functions.get_supervisee(super_ssn, connection)
        if supervisees:
            for i,supervisee in enumerate(supervisees):
                plt.figure(figsize=(6, 3))
                tasks, progress = functions.employee_progress(supervisees[i], connection)
                
                # Retrieve deadlines for tasks
                cursor = connection.cursor()
                cursor.execute("SELECT TNAME, DEADLINE FROM EMPLOYEE_TASK1 WHERE ESSN = %s", (supervisees[i],))
                task_deadlines = dict(cursor.fetchall())
                cursor.close()
                
                # Plot bars with legends for deadlines
                bars = plt.bar(tasks, progress, width=0.2, color='green')
                plt.xlabel('Tasks')
                
                plt.ylabel('Progress (%)')
                plt.title(f'Progress for {names[i]}')
                plt.ylim(0, 100)
                
                # Add legends for deadlines
                legends = [plt.Line2D([0], [0], color='white', linewidth=0, marker='o', markerfacecolor='white',
                                      markersize=10, label=f'{task}: {deadline}') for task, deadline in task_deadlines.items()]
                plt.legend(handles=legends, loc='best')
                
                plt.tight_layout()
                plt.savefig(f'static/progress_{i+1}.png')
                plt.close()


        plt.figure(figsize=(6, 3))
        manager_tasks, manager_progress = functions.employee_progress(super_ssn, connection)
        
        # Retrieve deadlines for manager tasks
        cursor = connection.cursor()
        cursor.execute("SELECT TNAME, DEADLINE FROM EMPLOYEE_TASK1 WHERE ESSN = %s", (super_ssn,))
        manager_task_deadlines = dict(cursor.fetchall())
        cursor.close()
        
        plt.bar(manager_tasks, manager_progress, width=0.5, color='purple')
        plt.xlabel("Tasks")
        #plt.xticks(range(len(manager_tasks)), manager_tasks, rotation=45)
        plt.ylabel("Progress (%)")
        plt.title("My progress")
        plt.ylim(0, 100)
        
        # Add legends for manager deadlines
        manager_legends = [plt.Line2D([0], [0], color='white', linewidth=0, marker='o', markerfacecolor='white',
                                      markersize=10, label=f'{task}: {deadline}') for task, deadline in manager_task_deadlines.items()]
        plt.legend(handles=manager_legends, loc='best')
        
        plt.tight_layout()
        plt.savefig(f'static/progress_manager.png')
        plt.close()

        connection.close()
        if functions.is_manager(super_ssn):
            return render_template("index2.html", num_supervisees=len(supervisees), session_logged_in= True, isManager = True)
        else:
            return render_template("index2.html", num_supervisees=len(supervisees), session_logged_in= True, isManager = False)
        
        

@app430.route('/reports',methods=['POST', 'GET'])
def reports():
    if request.method == 'POST':
        # Handle rating submission
        ssn = request.form['ssn']
        pnumber = request.form['pnumber']
        rating = int(request.form['rating'])

        conn = functions.get_db_connection()
        cursor = conn.cursor()
        app430.config["rating_success"] = True
        try:
            cursor.execute("INSERT INTO project_ratings (ssn, pnumber, rating) VALUES (%s, %s, %s)", (ssn, pnumber, rating))
            conn.commit()
            #flash('Rating submitted successfully!', 'success')  # Flash success message

        except psycopg2.Error as e:
            conn.rollback()
            app430.config["rating_success"] = False
            #flash(f"Error submitting rating: {e}", 'error')  # Flash error message
        finally:
            conn.close()
    
    average_salary_per_department = functions.compute_average_salary_per_department()
    female_count_per_department = functions.compute_female_count_per_department()
    gender_distribution_per_department = functions.compute_gender_distribution_per_department()

    # Generate plots using data
    plot_data_bar = functions.generate_plot_bar(average_salary_per_department)
    plot_data_pie = functions.generate_plot_pie(female_count_per_department)
    plot_data = functions.generate_plot_gender_distribution(gender_distribution_per_department)

    # Pass the encoded plot data to the template
    return render_template('report.html', plot_data_bar=plot_data_bar, plot_data_pie=plot_data_pie, plot_data=plot_data, rating_success = app430.config["rating_success"])

@app430.route('/submit_rating', methods=['POST'])
def submit_rating():
    ssn = request.form['ssn']
    pnumber = request.form['pnumber']
    rating = int(request.form['rating'])
    conn = functions.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO project_ratings (ssn, pnumber, rating) VALUES (%s, %s, %s)", (ssn, pnumber, rating))
        conn.commit()
        app430.config["rating_success"] = True 
        #flash('Rating submitted successfully!', 'success')  # Flash success message
    except psycopg2.Error as e:
        conn.rollback()
        app430.config["rating_success"] = False 
        #flash(f"Error submitting rating: {e}", 'error')  # Flash error message
    finally:
        conn.close()

    return redirect('/reports') 

@app430.route('/report_page', methods=['POST'])
def report_page():
    average_salary_per_department = functions.compute_average_salary_per_department()
    female_count_per_department = functions.compute_female_count_per_department()
    gender_distribution_per_department = functions.compute_gender_distribution_per_department()

    # Generate plots using data
    plot_data_bar = functions.generate_plot_bar(average_salary_per_department)
    plot_data_pie = functions.generate_plot_pie(female_count_per_department)
    plot_data = functions.generate_plot_gender_distribution(gender_distribution_per_department)

    # Pass the encoded plot data to the template
    return render_template('report.html', plot_data_bar=plot_data_bar, plot_data_pie=plot_data_pie, plot_data=plot_data, rating_success = app430.config["rating_success"])

###############################################################################################################################

##################################################TRANSLATION##################################################################
app430.config['UPLOAD_FOLDER'] = 'uploads/'
app430.config['ALLOWED_EXTENSIONS'] = {'txt'}

# Ensure the upload folder exists
os.makedirs(app430.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app430.config['ALLOWED_EXTENSIONS']

@app430.route('/translate')
def translate():
    if functions.is_manager(session['username']):
        return render_template('translate.html', session_logged_in = True, isManager= True, download_ready = False, translated=False)
    else:
        return render_template('translate.html', session_logged_in = True, isManager= False, download_ready = False, translated=False)

@app430.route('/download')
def download():
    filename = 'translated.txt'  
    safe_path = os.path.join("translated", filename)
    if not os.path.exists(safe_path):
        abort(404)
    return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path), as_attachment=True)

@app430.route('/upload-file', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = os.path.join(app430.config['UPLOAD_FOLDER'], 'uploads.txt')
        file.save(filename)
        
    path = "uploads/uploads.txt"
    f1 = open(path, 'rb')
    text = f1.read().decode(encoding="utf-8")
    translated = GoogleTranslator(source='auto', target='ar').translate(text)
    f1.close() 

    f2 = open("translated/translated.txt", "w", encoding="utf-8")
    f2.write(translated)
    f2.close()
    return render_template("translate.html",session_logged_in = True, download_ready = True, translated=False)

@app430.route('/submit-text', methods=['POST'])
def submit_text():
    text = request.form.get('text')
    translated = GoogleTranslator(source='auto', target="ar").translate(text)
    return render_template("translate.html", translated = translated, session_logged_in = True, download_ready = False)

###############################################################################################################################

if __name__ == '__main__':
    app430.run()

