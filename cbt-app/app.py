from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    attempted = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    correct_answer = db.Column(db.String(1))  # 'A', 'B', 'C'

# Create DB and seed questions and users
with app.app_context():
    db.create_all()
    if not Question.query.first():
        questions = [
    # Book of Acts
    Question(text="Who replaced Judas Iscariot as the twelfth apostle?", option_a="Barnabas", option_b="Matthias", option_c="Stephen", correct_answer="B"),
    Question(text="What miraculous event occurred on the day of Pentecost?", option_a="Jesus ascended to heaven", option_b="The disciples spoke in tongues", option_c="The temple veil was torn", correct_answer="B"),
    Question(text="What was the name of the man healed at the Beautiful Gate?", option_a="Simon", option_b="Bartimaeus", option_c="Not named", correct_answer="C"),
    Question(text="Who held the clothes of those who stoned Stephen?", option_a="Paul", option_b="Saul", option_c="Peter", correct_answer="B"),
    Question(text="Which apostle baptized the Ethiopian eunuch?", option_a="Philip", option_b="Peter", option_c="Paul", correct_answer="A"),
    Question(text="What was Paul's name before conversion?", option_a="Simon", option_b="Saul", option_c="Stephen", correct_answer="B"),
    Question(text="Where was Saul going when he encountered Jesus?", option_a="Antioch", option_b="Damascus", option_c="Jerusalem", correct_answer="B"),
    Question(text="What happened to Ananias and Sapphira?", option_a="They were exiled", option_b="They repented", option_c="They died", correct_answer="C"),
    Question(text="Who was the first Gentile to receive the Holy Spirit?", option_a="Cornelius", option_b="Timothy", option_c="Lydia", correct_answer="A"),
    Question(text="Where were believers first called Christians?", option_a="Jerusalem", option_b="Antioch", option_c="Rome", correct_answer="B"),

    # Why Revival Tarries
    Question(text="According to Ravenhill, what is the missing element in many churches?", option_a="Music", option_b="Prayer", option_c="Preaching", correct_answer="B"),
    Question(text="What does Ravenhill say revival tarries because of?", option_a="Lack of evangelism", option_b="Lack of Bibles", option_c="Lack of brokenness", correct_answer="C"),
    Question(text="What did Ravenhill refer to as the ‘secret’ of power?", option_a="Fasting", option_b="Prayer", option_c="Preaching", correct_answer="B"),
    Question(text="According to Ravenhill, where does revival begin?", option_a="In the church building", option_b="With leadership", option_c="In the heart of man", correct_answer="C"),
    Question(text="What kind of preaching does Ravenhill emphasize?", option_a="Prosperity", option_b="Repentance", option_c="Motivational", correct_answer="B"),
    Question(text="Ravenhill said, 'The church used to be a lifeboat, now it’s a...'", option_a="Cruise ship", option_b="Battleship", option_c="Fishing boat", correct_answer="A"),
    Question(text="What is essential for spiritual awakening, as per Ravenhill?", option_a="Planning", option_b="Praying men", option_c="Publicity", correct_answer="B"),
    Question(text="What does Ravenhill say is the greatest tragedy?", option_a="Sin in the world", option_b="Unrepentant believers", option_c="A sick church in a dying world", correct_answer="C"),
    Question(text="Which biblical character does Ravenhill say we need more of?", option_a="Elijah", option_b="David", option_c="John", correct_answer="A"),
    Question(text="Why does revival tarry, according to the book?", option_a="We are too lazy", option_b="The altar is too clean", option_c="We are content without it", correct_answer="C")
]
        db.session.add_all(questions)
        db.session.commit()

    # Register students
    student_names = [
    "Alao Victor Oluwatayemise",
    "AKERELE Ifedayo David",
    "ADEYEMO Olalekan",
    "OGEDENGBE John",
    "ODEJOBI Deborah",
    "OYEKALE Susannah",
    "OGUNSOLA Toluwaniyin",
    "OJO Kehinde",
    "OLATUNJI Victor",
    "ISHOLA Tolamise",
    "Olaniyi Oluwafunbi",
    "ADEKOYA KEHINDE OLUWASEUN",
    "Ojediran Jeremiah"
]

    for name in student_names:
        if not User.query.filter_by(username=name).first():
            db.session.add(User(username=name, password=name))
    db.session.commit()

# Home/Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password.lower() == password.lower():
            session['user_id'] = user.id
            if user.attempted:
                return "You have already attempted this exam."
            return redirect(url_for('exam'))
        return "Invalid credentials."
    return render_template('login.html')

# Exam Page
@app.route('/exam')
def exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    questions = Question.query.all()
    return render_template('exam.html', questions=questions)

# Submit Exam
@app.route('/submit', methods=['POST'])
def submit():
    user = User.query.get(session['user_id'])
    questions = Question.query.all()
    score = 0
    for q in questions:
        user_answer = request.form.get(f'q{q.id}')
        if user_answer == q.correct_answer:
            score += 1
    user.score = score
    user.attempted = True
    db.session.commit()
    session.pop('user_id', None)
    return render_template('result.html', score=score, total=len(questions))

# Admin view to see all scores
@app.route('/admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)

"""
templates/admin.html
---------------------
<!DOCTYPE html>
<html>
<head><title>Admin - Results</title></head>
<body>
    <h2>Exam Results</h2>
    <table border="1">
        <tr>
            <th>Full Name</th>
            <th>Score</th>
            <th>Attempted</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.username }}</td>
            <td>{{ user.score }}</td>
            <td>{{ 'Yes' if user.attempted else 'No' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""
