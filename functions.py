import psycopg2
import bcrypt
import matplotlib.pyplot as plt
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
import io,os
import base64

# Database connection details
DB_NAME = "430company"
DB_USER = "postgres"
DB_PASSWORD = "hello"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"


# Function to establish database connection
def get_db_connection():
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def signup(username,password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()

        cur.close()
        conn.close()
        print("Signup successful!")
    except Exception as e:
        print("Error:", e)

def authenticate_user(username, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Retrieve the hashed password associated with the username
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        hashed_password = cur.fetchone()

        if hashed_password:
            # Check if the provided password matches the hashed password
            if bcrypt.checkpw(password.encode(), hashed_password[0].encode()):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print("Error:", e)
        return False

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    if authenticate_user(username, password):
            print("Login successful!")
    else:
        print("Login failed.")

def is_manager(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employee WHERE super_ssn = %s", (username,))
        count = cursor.fetchone()[0]
        if count > 0:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        conn.close()


def check_ssn_exists(ssn):
    """Check if an SSN exists in the employee database table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Use a parameterized query to prevent SQL injection
        cursor.execute("SELECT COUNT(*) FROM employee WHERE ssn = %s", (ssn,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        if conn:
            conn.close()

# Example usage:
ssn_to_check = "123-45-6789"
exists = check_ssn_exists(ssn_to_check)
print("SSN exists:", exists)


def insert_new_employee(conn, cursor, fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, attendance, life_cycle, position):
    try:
        cursor.execute("INSERT INTO employee(fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, attendance, life_cycle, position) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)",
                       (fname, minit, lname, ssn, address, sex, salary, super_ssn, dno, attendance, life_cycle, position))
        conn.commit()
        print("Employee successfully added")
        return False
    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting employee:", e)
        return True

def insert_new_task(conn, cursor, tname,essn,deadline,description,total_hours,required_hours):
    try:
        cursor.execute("INSERT INTO EMPLOYEE_TASK1 VALUES (%s,%s,%s,%s,%s,%s)",(tname,essn,deadline,description,total_hours,required_hours))
        conn.commit()
        print("Task successfully added")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting task:", e)
        return False

def insert_new_empskill(conn,cursor,essn,skill):
    try:
        cursor.execute("INSERT INTO EMPLOYEE_SKILLS VALUES (%s,%s)",(essn,skill))
        conn.commit()
        print("Skill successfully added to employee")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting skill into employee:", e)
        return False

def insert_new_emproject(conn, pname, pno, location, deadline, budget, department):
    try:
        cursor = conn.cursor()    
        cursor.execute("INSERT INTO project VALUES (%s,%s,%s,%s,%s,%s)", (pname, pno, location, department, deadline, budget))
        conn.commit()
        print("Project successfully added to employee")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting project into employee:", e)
        return False 
    finally:
        cursor.close()


def insert_workhours(conn,cursor,ssn,work_date,total_hours):
    try:
        cursor.execute("INSERT INTO Employee_Work_Log (ssn,work_date,total_hours) VALUES (%s,%s, %s)", (ssn, work_date, total_hours))
        conn.commit()
        print("Working hours successfully added to employee")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print("Error inserting working hours for employee:", e)
        return False

def insert_project_skills(pno,skills):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for s in skills:
            cursor.execute("INSERT INTO PROJECT_SKILL VALUES (%s,%s)",(pno,s))
        return True
    except psycopg2.Error as e:
        conn.rollback()
        return False

def skill_matching(skills):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholders = ', '.join(['%s'] * len(skills))
        cursor.execute(
            f"SELECT E.SSN, E.FNAME, E.LNAME FROM EMPLOYEE E JOIN EMPLOYEE_SKILLS ES ON E.SSN = ES.ESSN WHERE ES.SKILL ILIKE ANY (ARRAY[{placeholders}])",
            [f"%{skill}%" for skill in skills])
        employees = cursor.fetchall()
        return employees
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        conn.close()

def add_employees_to_project(ssn_selected_employees, pno):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Iterate over selected employees' SSNs and insert them into EMPLOYEE_PROJECT table
        for ssn in ssn_selected_employees:
            cursor.execute("INSERT INTO EMPLOYEE_PROJECT (ESSN, PNO) VALUES (%s, %s)", (ssn, pno))
        conn.commit()
        return True
    except Exception as e:
        print("Error:", e)
        conn.rollback() 
        return False
    finally:
        conn.close()

def get_supervisee(super_ssn, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT SSN, FNAME FROM EMPLOYEE WHERE SUPER_SSN = %s", (super_ssn,))
    results = cursor.fetchall()
    names = [r[1] for r in results]
    supervisees = [r[0] for r in results]
    cursor.close()
    return supervisees, names

def get_employee_progress(employee_ssn, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT TNAME, STATUS FROM EMPLOYEE_TASK1 WHERE ESSN = %s", (employee_ssn,))
    results = cursor.fetchall()
    tasks_name = [r[0] for r in results]
    tasks_progress = [r[1] for r in results]
    cursor.close()
    return tasks_name, tasks_progress



######################GRAPHS####################
# Function to compute average salary per department
def compute_average_salary_per_department():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT dno, AVG(salary) FROM employee GROUP BY dno")
    average_salary_per_department = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return average_salary_per_department

# Function to compute the number of females per department
def compute_female_count_per_department():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT dno, COUNT(*) FROM employee WHERE sex = 'F' GROUP BY dno")
    female_count_per_department = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return female_count_per_department



# Function to compute gender distribution per department
def compute_gender_distribution_per_department():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dno, 
               SUM(CASE WHEN sex = 'M' THEN 1 ELSE 0 END) AS male_count,
               SUM(CASE WHEN sex = 'F' THEN 1 ELSE 0 END) AS female_count
        FROM employee
        GROUP BY dno
    """)
    gender_distribution_per_department = {row[0]: {'Male': row[1], 'Female': row[2]} for row in cursor.fetchall()}

    conn.close()
    return gender_distribution_per_department

def generate_plot_bar(average_salary_per_department):
    departments = list(average_salary_per_department.keys())
    average_salaries = list(average_salary_per_department.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(departments, average_salaries, color=COLORS)
    plt.xlabel('Department Number')
    plt.ylabel('Average Salary')
    plt.title('Average Salary per Department')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar, salary in zip(bars, average_salaries):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{salary:.2f}', 
                 ha='center', va='bottom')
        
    plt.xticks(departments)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data_bar = base64.b64encode(buffer.getvalue()).decode()

    return plot_data_bar

def generate_plot_pie(female_count_per_department):
    departments = list(female_count_per_department.keys())
    female_percentages = [(female_count_per_department.get(d, 0) / len(departments)) * 100 for d in departments]

    plt.figure(figsize=(8, 8))
    plt.pie(female_percentages, labels=departments, autopct='%1.1f%%', startangle=140, colors=COLORS)
    plt.title('Female Percentage per Department')

    for department, percentage in zip(departments, female_percentages):
        plt.text(0, 0, f'{female_count_per_department.get(department, 0)}', color='white', fontsize=12, ha='center', va='center')

    buffer_pie = io.BytesIO()
    plt.savefig(buffer_pie, format='png')
    buffer_pie.seek(0)
    plot_data_pie = base64.b64encode(buffer_pie.getvalue()).decode()

    return plot_data_pie

def generate_plot_gender_distribution(gender_distribution_per_department): 
    departments = list(gender_distribution_per_department.keys())
    male_counts = [data['Male'] for data in gender_distribution_per_department.values()]
    female_counts = [data['Female'] for data in gender_distribution_per_department.values()]

    plt.figure(figsize=(10, 6))
    plt.bar(departments, male_counts, color='#1f77b4', label='Male')
    plt.bar(departments, female_counts, bottom=male_counts, color='#ff7f0e', label='Female')
    plt.xlabel('Department Number')
    plt.ylabel('Number of Employees')
    plt.title('Distribution of Male and Female Employees per Department')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(departments)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return plot_data

def get_supervisee(super_ssn, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT SSN, FNAME FROM EMPLOYEE WHERE SUPER_SSN = %s", (super_ssn,))
    results = cursor.fetchall()
    names = [r[1] for r in results]
    supervisees = [r[0] for r in results]
    cursor.close()
    return supervisees, names

def employee_progress(employee_ssn, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT TNAME, REQUIRED_HOURS, TOTAL_HOURS FROM EMPLOYEE_TASK1 WHERE ESSN = %s", (employee_ssn,))
    results = cursor.fetchall()
    tasks_name = [r[0] for r in results]
    
    # Calculate progress percentage for each task
    tasks_progress = [(r[2] / r[1]) * 100 if r[1] != 0 else 0 for r in results]  # Avoid division by zero
    cursor.close()
    return tasks_name, tasks_progress


def delete():
    for file in os.listdir('static'):
        if file.startswith('progress_') or file == 'progress_manager.png':
            os.remove(os.path.join('static', file))
    return ""


