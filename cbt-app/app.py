from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    correct_answer = db.Column(db.String(1))

@app.route('/track-tab', methods=['POST'])
def track_tab():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user.tab_switches += 1
            user.last_tab_switch = datetime.datetime.now()
            db.session.commit()
            return jsonify({"status": "updated"}), 200
    return jsonify({"status": "unauthorized"}), 401

with app.app_context():
    db.create_all()

    if not Question.query.first():
        # Add your question_data list here
        question_data =  [
            # Original 40 questions
            ("God's infallible WORD teaches & we believe:", "Bible doctrines", "Discipleship teachings", "Repentance only", "A"),
            ("What is Bible doctrine 5?", "The Godhead", "Repentance", "Justification", "A"),
            ("The Bible is _____", "God's will", "God's word", "God's own", "B"),
            ("____ will occur after the rapture.", "Justification", "The Great tribulation", "Peace & Joy in the world", "B"),
            ("What is Bible doctrine 8?", "The Lord's supper", "Water baptism", "The Holy Bible", "B"),
            ("Is Bible doctrine 3 known to be 'The Virgin birth of Jesus'?", "False", "True", "None of the above", "B"),
            ("The redeemed shall dwell with _____ forever.", "satan", "spirit", "God", "C"),
            ("_____ was prepared for the devil & his angels.", "Punishment", "evils", "hell fire", "C"),
            ("The Bible teaches that man is totally depraved.", "Yes", "No", "Yes & no", "A"),
            ("Where is God expecting you to spend eternity with HIM?", "Heaven", "Hell", "the world", "A"),
            ("The last session of the Bible doctrine is known as", "Revelations", "Eschatology", "Eternity", "B"),
            ("What is Bible doctrine 1?", "The Godhead", "The Holy Bible", "Restitution", "B"),
            ("______ is the act of God's grace whereby one's sins are forgiven...", "Restitution", "Righteousness", "Justification", "C"),
            ("The Bible teaches that Jesus Christ was born of a virgin.", "False", "True", "partially correct", "B"),
            ("What is Bible doctrine 15?", "The rapture", "Repentance", "Restitution", "A"),
            ("What is the last Bible doctrine focused on?", "Hell fire", "Rapture", "Heaven", "C"),
            ("How many Bible doctrines have we?", "24", "20", "22", "C"),
            ("What is Bible doctrine 12?", "Redemption healing and health", "Entire sanctification", "Prayer", "A"),
            ("The Holy Bible consists of_____ books of the New Testament.", "39", "37", "27", "C"),
            ("Bible doctrine 9 is", "The Lord's supper", "Heaven", "Eternity", "A"),
            ("Fasting is an optional activity for a Christian.", "True", "False", "", "B"),
            ("The first account of the disciples receiving the Holy Ghost baptism...", "Acts 1:8", "Acts 2:1–4", "Mark 16:15", "B"),
            ("'Love not the world...' can be found where?", "John 15:1", "1 John 3:1", "1 John 2:15", "C"),
            ("All but one of the following hinders an effective quiet time:", "Dancing", "Gluttony", "Fatigue", "A"),
            ("The following are hindrances to benefiting from the Bible except:", "Unbelief", "Double-mindedness", "Reading", "D"),
            ("'Fishers of men' is a figurative expression meaning:", "Catching fishes", "Soul winning", "Quiet time", "B"),
            ("One of these is not a definition of sanctification:", "Removal of sin", "Holiness", "The third work of grace", "C"),
            ("Justification comes after:", "Sinning", "Salvation", "Sanctification", "B"),
            ("Which of these should we give less priority to?", "Spiritual life", "Skill acquisition", "Social media", "D"),
            ("The property in church should be treated as our own.", "True", "False", "", "A"),
            ("Which is not a gift of the Spirit?", "Gentleness", "Faith", "Working of miracles", "A"),
            ("Way God can speak to us in knowing His will in marriage:", "Cohabitating", "Deep love", "Through a prophet", "B"),
            ("Another name for pseudo-Christianity is:", "Sudden Christianity", "False Christianity", "Imperfect Christianity", "B"),
            ("The knowledge of homiletics is needed for every Christian.", "True", "False", "", "A"),
            ("God is interested in our finances as our spiritual life.", "No", "Sometimes", "Yes", "D"),
            ("All but one is a gesture to avoid with opposite gender:", "Hugging", "Isolated places", "Sitting close", "C"),
            ("Fasting must be accompanied by one of these:", "Shouting", "Praying", "Listening", "B"),
            ("Not a prerequisite for receiving Holy Ghost baptism:", "Salvation", "Sanctification", "Gymnastics", "C"),
            ("Worldliness is okay for me:", "No", "Yes", "Sometimes", "A"),
            ("An example of Christian dressing:", "Tight trousers", "Jewelry", "Moderate trousers", "E"),

            # New 20 questions (Acts + Ravenhill)
            ("Who replaced Judas Iscariot as a disciple?", "Matthias", "Barnabas", "Stephen", "A"),
            ("Where did the Holy Spirit descend on the apostles?", "Upper Room", "Synagogue", "Temple", "A"),
            ("What appeared over the apostles' heads on Pentecost?", "Smoke", "Flames", "Water", "B"),
            ("What was Paul's original name?", "Simon", "Saul", "Silas", "B"),
            ("Who was stoned while Paul watched?", "Stephen", "Barnabas", "Peter", "A"),
            ("Where was Paul when he encountered Jesus?", "Damascus", "Jerusalem", "Rome", "A"),
            ("Who healed the lame man at the temple gate?", "Peter & John", "Paul", "Stephen", "A"),
            ("How many people were added to the church on Pentecost?", "3000", "120", "5000", "A"),
            ("What was the name of the sorcerer in Acts 8?", "Simon", "Elymas", "Bar-Jesus", "A"),
            ("What was Paul's profession?", "Fisherman", "Tentmaker", "Carpenter", "B"),
            ("Why does Ravenhill say revival tarries?", "Because people don't pray", "Because God delays", "Because of politics", "A"),
            ("What does Ravenhill call the missing element in modern preaching?", "Humor", "Anointing", "Fire", "C"),
            ("What must a man do before God will use him mightily?", "Be educated", "Be broken", "Be famous", "B"),
            ("What did Ravenhill say the church lacks today?", "Strategy", "Power", "Money", "B"),
            ("What kind of men does God use?", "Gifted men", "Smart men", "Broken men", "C"),
            ("What did Ravenhill say we need more than revival meetings?", "Prayer meetings", "Miracles", "Money", "A"),
            ("What is the devil not afraid of?", "Programs", "Holy men", "Fasting", "A"),
            ("Where did Ravenhill say true revival starts?", "In churches", "In seminars", "In hearts", "C"),
            ("What makes a sermon powerful, according to Ravenhill?", "Length", "Delivery", "Burden", "C"),
            ("Ravenhill said, 'The church used to be a lifeboat, now it’s a...'", "Cruise ship", "Battleship", "Fishing boat", "A")
        ]

        questions = [
            Question(text=q[0], option_a=q[1], option_b=q[2], option_c=q[3], correct_answer=q[4])
            for q in question_data
        ]
        db.session.add_all(questions)
        db.session.commit()

    student_names = [
    "Alao Victor Oluwatayemise", "John Doe", "Jane Smith", "Peter Johnson", "Mary Adams", "Samuel Oladele", "Grace Adebayo",
    "Daniel Okonkwo", "Mercy Omotola", "Emmanuel Adeola", "Deborah Oke", "David Benson", "Esther Akande",
    "OLAOYE Oluwadarasimi", "OYATUNDE DAMILOLA IREMIDE", "Oyedemi Emmanuel Oyeleke", "AKHIGBE Prevail Caleb",
    "Olanrewaju Isaiah", "OLATUNJI Emmanuel Oladeji", "ADELEKE PETER INIOLUWA", "PAUL", "AKINOlA Faith Testimony",
    "Israel Temiloluwa OGUNSOLA", "Adikwu John", "Adebayo Victor Oluwabori", "ADENIRAN TEMIDAYO PRAISE",
    "AFOLABI john ayomide", "Ojo Rebecca Oluwafunmilola", "AJALA Caleb", "ADEWALE Jerry Ayomide", "AYOOLA BLESSING TITILADE",
    "Oyebade Blessing Oluwapelumi", "OYEBOLA Ireoluwa Jeremiah", "MATTHEW Faith", "ERONMOSELE SHALOM OSETOKHAME",
    "ABIMBOLA GOODNESS OLUDAMOLA", "AKINWUMI Blessing Olajumoke", "OYEDEMI Favour Ayomikun", "ADISA STEPHEN BABAFEMI",
    "KILANKO Oluwatobiloba .D.", "AYOOLA Bolanle", "OLAGOKE DANIEL OLORUNFEMI", "ABIMBOLA Hismercy Toluwani",
    "OKEDI FAVOUR OGHENETEGA", "Awodele Elizabeth praise", "SANUSI Kehinde johanah", "OLUWANIMBE Faithful Oluwadara",
    "OYEBOLA Oreoluwa James", "BABALOLA Jeremiah Iniolu", "OLALEYE OLOLADE DEBORAH", "AJALA JERRY OLUWASEUN",
    "OWOLABI OLAMIDE PEACE", "OLUFEMI Joel Seyi", "AJAYI Goodness Paul", "Adetunji Promise Ayomikun",
    "OWOLAWASE Simeon Olajide", "AJAYI ELIJAH OLUWASEGUN", "AYANTUNDE Patience Omowumi", "ALAGBE ABIGEAL ADEBOLA",
    "OLADIPUPO Paul Segun", "AREMU KEMI TAIWO", "ADEJUMO Joshua Oluwadamilare", "Aderanti Adesewa Grace",
    "Olugbade ComFort", "AJIBADE TOLUWALASE PRAISE", "GODWIN PRAISE OBOR", "OJOELE Oluwaseun Ruth",
    "Olajide David Oluwaferanmi", "OLAMOYEGUN Oluwadamilola Dolapo", "ADEWUMI Deborah Ayomide", "JOEL Favour",
    "OYEKUNLE Marcus Timileyin", "OYADIRAN Dorcas oluwadamisi", "OLAYANJU Archippus Oladayo", "ADEGOKE, Praise Moyinoluwa",
    "AGBOOLA FAVOUR ADEKEMI", "ADEBISI Feranmi Eunice", "ISHOLA Emmanuel Iseoluwa", "KOLAWOLE VICTORY ATINUKE",
    "ALABI DEBORAH INIOLUWA", "ISAIAH Adebayo Adeeyo", "MATTHEW Precious Ibukunoluwa", "OYELEYE Gladys Oluwajuwonlo",
    "ODEBOWALE", "ANWO HERITAGE OLUWADAMILOLA", "ABOLADE MARVELLOUS OLAYEMI", "Bamigboye Joshua boluwatife",
    "OCHIMANA Elijah Iko-Ojo", "OKE FAVOUR OLUWASEYI", "ADEGOKE", "OLANREWAJU MAYOWA JOHN", "OLADOJA GOD'SGLORY AYANFE",
    "Olaniran dorcas omolara", "OLADELE Abosede", "Bolarinwa Janet", "SHALOM GBADEBO OLUWAFEYISARA",
    "Raphael Temitope Good luck", "ADEBUNMI SUCCESS ADEOLA", "OGUNLADE Excellence", "AKERELE Ifedayo David",
    "Pearl David", "Ogundele Eunice", "Adebayo Enoch", "Ireoluwa Oyebola Jeremiah", "Aderibigbe, Marvellous Aduragbemi", "Adediran Victoria Oluwatobi"
]  
    for name in student_names:
        if not User.query.filter_by(username=name).first():
            hashed_pw = generate_password_hash(name)
            db.session.add(User(username=name, password=hashed_pw))
    db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, username):
            session['user_id'] = user.id
            return redirect(url_for('exam'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.attempted:
        return "You have already attempted the exam."

    questions = Question.query.all()
    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.form.get(str(q.id))
            if selected == q.correct_answer:
                score += 1
        user.score = score
        user.attempted = True
        db.session.commit()
        return render_template('result.html', score=score, total=len(questions))

    return render_template('exam.html', questions=questions)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'DLCF' and password == 'excos':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid admin credentials')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
