from optparse import Values

from flask import Flask, render_template, request, jsonify
import mysql.connector
import pickle
import traceback
import numpy as np

app = Flask(__name__)

# ================= MYSQL CONNECTION =================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234567",
    database="placement_db"
)

cursor = db.cursor(dictionary=True)

# ================= HOME PAGE =================

@app.route('/')
def home():
    return render_template('mainpage.html')

# ================= PREDICTION PAGE =================

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

# ================= PREDICT FUNCTION =================
@app.route('/predict', methods=['POST'])
def predict():
    try:

        # ================= FORM DATA =================
        name = request.form['name']
        roll_no = request.form['roll_no']
        course = request.form['course']
        subcourse = request.form['subcourse']

        cgpa = float(request.form['cgpa'])
        attendance = float(request.form['attendance'])
        internships = int(request.form['internships'])
        technical = float(request.form['technical'])
        communication = float(request.form['communication'])
        backlogs = int(request.form['backlogs'])

        # ================= MODEL =================
        model = pickle.load(open('placement_model.pkl', 'rb'))

        features = np.array([[
            cgpa,
            attendance,
            internships,
            technical,
            communication,
            backlogs
        ]])

        prediction = model.predict(features)[0]

        try:
            probability = round(
                model.predict_proba(features)[0][1] * 100,
                2
            )
        except:
            probability = 50.0

        placed = int(prediction)

        # ================= AI EXPLANATION LOGIC (ADDED) =================
        reasons = []

        if cgpa < 6:
            reasons.append("Low CGPA")
        if attendance < 75:
            reasons.append("Low Attendance")
        if internships == 0:
            reasons.append("No Internship Experience")
        if technical < 6:
            reasons.append("Weak Technical Skills")
        if communication < 6:
            reasons.append("Poor Communication Skills")
        if backlogs > 0:
            reasons.append("Backlogs Present")

        if placed == 1:
            message = "Congratulations! You are likely placed."
        else:
            message = "Placement chance is low."
            if reasons:
                message += " Reasons: " + ", ".join(reasons)

        # ================= DATABASE (ONLY NUMERIC DATA) =================
        sql = """
      INSERT INTO student_data
  (
    name,
    roll_no,
    course,
    subcourse,
    cgpa,
    attendance,
    internships,
    technical_skills,
    communication_skills,
    technical,
    communication,
    backlogs,
    placement_status,
    placed,
    probability
   )
   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
        values = (
            name,
            roll_no,
            course,
            subcourse,
            cgpa,
            attendance,
            internships,
            technical,
            communication,
            technical,
            communication,
            backlogs,
            placed,
            placed,
            probability
        )
        cursor.execute(sql, values)
        db.commit()

        # ================= RESULT PAGE =================
        return render_template(
            'result.html',
            name=name,
            roll_no=roll_no,
            course=course,
            subcourse=subcourse,
            probability=probability,
            placed=placed,
            message=message,
            cgpa=cgpa,
            attendance=attendance,
            technical=technical,
            communication=communication
        )

    except Exception as e:
        traceback.print_exc()
        return f"ERROR : {e}"
# ================= DASHBOARD =================

@app.route('/dashboard')
def dashboard():
    db.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM student_data")
    total_students = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS placed FROM student_data WHERE placement_status = 1")
    placed_students = cursor.fetchone()['placed']

    not_placed = total_students - placed_students

    placement_rate = 0
    if total_students > 0:
        placement_rate = round((placed_students / total_students) * 100, 2)

    cursor.execute("""
        SELECT *
        FROM student_data
        ORDER BY id DESC
    """)
    students = cursor.fetchall()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        placed_students=placed_students,
        not_placed=not_placed,
        placement_rate=placement_rate,
        students=students
    )

# ================= GRAPH PAGE =================

@app.route('/graph')
def graph():
    return render_template('graph.html')

# ================= GRAPH DATA =================

@app.route('/graph-data')
def graph_data():
    db.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM student_data")
    total_students = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS placed 
        FROM student_data 
        WHERE placement_status = 1
    """)

    placed_students = cursor.fetchone()['placed']

    not_placed = total_students - placed_students

    return jsonify({
        "placed": placed_students,
        "notPlaced": not_placed
    })


@app.route('/accuracy')
def accuracy():
    data = pickle.load(open("accuracy_data.pkl", "rb"))

    return render_template(
        "accuracy.html",
        accuracies=data["accuracies"],
        best_model=data["best_model"],
        best_accuracy=data["best_accuracy"]
    )



# ================= RUN APP =================

if __name__ == '__main__':
    app.run(debug=True)