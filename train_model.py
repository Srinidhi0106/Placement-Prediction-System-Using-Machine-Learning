import pandas as pd
import pickle
import mysql.connector

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# ================= MYSQL CONNECTION =================

db = mysql.connector.connect(
host="localhost",
user="root",
password="1234567",
database="placement_db"
)

# ================= LOAD DATA FROM MYSQL =================

query = """
SELECT
cgpa,
attendance,
internships,
technical_skills,
communication_skills,
backlogs,
placement_status
FROM student_data
"""

data = pd.read_sql(query, db)

# ================= FEATURES & TARGET =================

X = data[
[
"cgpa",
"attendance",
"internships",
"technical_skills",
"communication_skills",
"backlogs"
]
]

y = data["placement_status"]

# ================= TRAIN TEST SPLIT =================

X_train, X_test, y_train, y_test = train_test_split(
X,
y,
test_size=0.2,
random_state=42
)

# ================= MODELS =================

models = {
"Logistic Regression": LogisticRegression(max_iter=1000),
"Decision Tree": DecisionTreeClassifier(),
"KNN": KNeighborsClassifier(),
"Random Forest": RandomForestClassifier(),
"SVM": SVC(probability=True)
}

accuracies = {}

best_model_name = ""
best_accuracy = 0
best_model = None

# ================= TRAIN ALL MODELS =================

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions) * 100
    accuracies[name] = round(accuracy, 2)
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model_name = name
        best_model = model

# ================= SAVE BEST MODEL =================

pickle.dump(
best_model,
open("placement_model.pkl", "wb")
)

# ================= SAVE ACCURACY DATA =================

pickle.dump(
{
"accuracies": accuracies,
"best_model": best_model_name,
"best_accuracy": round(best_accuracy, 2)
},
open("accuracy_data.pkl", "wb")
)

# ================= OUTPUT =================

print("\nModel Accuracies:")
for model, accuracy in accuracies.items():
 print(f"{model}: {accuracy}%")

print("\nBest Model:", best_model_name)
print("Best Accuracy:", round(best_accuracy, 2), "%")
