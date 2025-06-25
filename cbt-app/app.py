from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = False

db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    attempted = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer)
    tab_switches = db.Column(db.Integer, default=0)
    last_tab_switch = db.Column(db.DateTime)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    correct_answer = db.Column(db.String(1))  # 'A', 'B', 'C'

# Create DB and seed data
with app.app_context():
    db.create_all()
    if not Question.query.first():
        questions = [
            Question(text="Who replaced Judas Iscariot as a disciple?", option_a="Matthias", option_b="Barnabas", option_c="Stephen", correct_answer="A"),
            Question(text="Where did the Holy Spirit descend on the apostles?", option_a="Upper Room", option_b="Synagogue", option_c="Temple", correct_answer="A"),
            Question(text="What appeared over the apostles' heads on Pentecost?", option_a="Smoke", option_b="Flames", option_c="Water", correct_answer="B"),
            Question(text="What was Paul's original name?", option_a="Simon", option_b="Saul", option_c="Silas", correct_answer="B"),
            Question(text="Who was stoned while Paul watched?", option_a="Stephen", option_b="Barnabas", option_c="Peter", correct_answer="A"),
            Question(text="Where was Paul when he encountered Jesus?", option_a="Damascus", option_b="Jerusalem", option_c="Rome", correct_answer="A"),
            Question(text="Who healed the lame man at the temple gate?", option_a="Peter & John", option_b="Paul", option_c="Stephen", correct_answer="A"),
            Question(text="How many people were added to the church on Pentecost?", option_a="3000", option_b="120", option_c="5000", correct_answer="A"),
            Question(text="What was the name of the sorcerer in Acts 8?", option_a="Simon", option_b="Elymas", option_c="Bar-Jesus", correct_answer="A"),
            Question(text="What was Paul's profession?", option_a="Fisherman", option_b="Tentmaker", option_c="Carpenter", correct_answer="B"),
            Question(text="Why does Ravenhill say revival tarries?", option_a="Because people don't pray", option_b="Because God delays", option_c="Because of politics", correct_answer="A"),
            Question(text="What does Ravenhill call the missing element in modern preaching?", option_a="Humor", option_b="Anointing", option_c="Fire", correct_answer="C"),
            Question(text="What must a man do before God will use him mightily?", option_a="Be educated", option_b="Be broken", option_c="Be famous", correct_answer="B"),
            Question(text="What did Ravenhill say the church lacks today?", option_a="Strategy", option_b="Power", option_c="Money", correct_answer="B"),
            Question(text="What kind of men does God use?", option_a="Gifted men", option_b="Smart men", option_c="Broken men", correct_answer="C"),
            Question(text="What did Ravenhill say we need more than revival meetings?", option_a="Prayer meetings", option_b="Miracles", option_c="Money", correct_answer="A"),
            Question(text="What is the devil not afraid of?", option_a="Programs", option_b="Holy men", option_c="Fasting", correct_answer="A"),
            Question(text="Where did Ravenhill say true revival starts?", option_a="In churches", option_b="In seminars", option_c="In hearts", correct_answer="C"),
            Question(text="What makes a sermon powerful, according to Ravenhill?", option_a="Length", option_b="Delivery", option_c="Burden", correct_answer="C"),
            Question(text="Ravenhill said, 'The church used to be a lifeboat, now it’s a...'", option_a="Cruise ship", option_b="Battleship", option_c="Fishing boat", correct_answer="A")
        ]
        db.session.add_all(questions)
        db.session.commit()

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
            hashed_pw = generate_password_hash(name)
            db.session.add(User(username=name, password=hashed_pw))
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.attempted:
                return "You have already attempted this exam."
            return redirect(url_for('exam'))
        return "Invalid credentials."
    return render_template('login.html')

@app.route('/exam')
def exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    questions = Question.query.all()
    return render_template('exam.html', questions=questions)

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

@app.route('/log_tab_switch', methods=['POST'])
def log_tab_switch():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.tab_switches += 1
        user.last_tab_switch = datetime.datetime.now()
        db.session.commit()
    return ('', 204)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
        return "Invalid admin login."
    return '''
    <form method="post">
        <input name="username" placeholder="Admin Username" required>
        <input name="password" placeholder="Password" type="password" required>
        <input type="submit">
    </form>
    '''

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin')
def admin_dashboard():
    users = User.query.all()
    return render_template('admin.html', users=users)


if __name__ == '__main__':
    app.run(debug=False)
