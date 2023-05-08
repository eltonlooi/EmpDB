from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/")
def loadPage():
    return render_template('AddEmp.html', img_path="static/img/")

@app.route("/addEmpOuput", methods=['GET', 'POST'])
def addEmpOutput():
    return render_template('AddEmpOutput.html', img_path="static/img/")

@app.route("/getEmp", methods=['GET', 'POST'])
def getEmp():
    return render_template('GetEmp.html', img_path="static/img/")

@app.route("/getEmpOutput", methods=['GET', 'POST'])
def getEmpOutput():
    return render_template('GetEmpOutput.html', img_path="static/img/")

@app.route("/addEmpHome", methods=['GET', 'POST'])
def addEmpHome():
    return render_template('AddEmp.html', img_path="static/img/")

@app.route("/addEmp", methods=['POST'])
def addEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    hire_date = request.form['hire_date']
    job_title = request.form['job_title']
    salary = request.form['salary']
    working_hour = request.form['working_hour']
    attandance = request.form['attandance']
    benefit = request.form["benefit"]
    
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, hire_date, job_title, salary, working_hour, attandance, benefit))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/fetchdata", methods=['GET','POST'])
def fetchInfo():    
    emp_id = request.form['emp_id']
    mycursor = db_conn.cursor()
    first_name = "N/A"
    last_name = "N/A"
    pri_skill = "N/A"
    location = "N/A"
    hire_date = "N/A"
    job_title = "N/A"
    salary = "N/A"
    working_hour = "N/A"
    attandance = "N/A"
    benefit = "N/A"
    emp_image = None
    try:
        mycursor.execute("SELECT * FROM employee WHERE emp_id = %s",(emp_id,))
        myresult = mycursor.fetchall()
        for row in myresult:
            first_name = row[1]
            last_name = row[2]
            pri_skill = row[3]
            location = row[4]
            hire_date = row[5]
            job_title = row[6]
            salary = row[7]
            working_hour = row[8]
            attandance = row[9]
            benefit = row[10]
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            
            s3_image_url ="https://{0}.s3.amazonaws.com/{1}/{2}".format(
                bucket,
                custombucket,
                emp_image_file_name_in_s3)
            return render_template('GetEmpOutput.html',
                                   id = emp_id, 
                                   fname =  first_name, 
                                   lname = last_name,
                                   pskill = pri_skill,  
                                   loc = location,
                                   hire = hire_date,
                                   job = job_title,
                                   salary = salary,
                                   hour = working_hour,
                                   att = attandance,
                                   ben = benefit,
                                   image = s3_image_url)
    except Exception as e:
            
        return render_template('GetEmpOutput.html',
                               id = emp_id, 
                               fname =  first_name, 
                               lname = last_name,
                               pskill = pri_skill,  
                               loc = location,
                               hire = hire_date,
                               job = job_title,
                               salary = salary,
                               hour = working_hour,
                               att = attandance,
                               ben = benefit,
                               image = s3_image_url)
    finally:
            
        mycursor.close()

            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


