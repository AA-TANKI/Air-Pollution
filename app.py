from flask import Flask, url_for, redirect, render_template, request, session
import sqlite3
import requests
from flask_socketio import SocketIO, emit
from datetime import datetime
from cs50 import SQL
# Constants
API = "8514297f19210d7907ff75d14206b803be101dd8"
BASE_URL = 'https://api.waqi.info/feed/'

# Flask App Initialization
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed to use sessions
socketio = SocketIO(app)
db = SQL("sqlite:///data.db")

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def home():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT city FROM user WHERE username = ?", (session["username"],))
        city_row = cursor.fetchone()
        city = city_row['city']
        cursor.execute("SELECT COUNT(*) FROM user WHERE city = ?", (city,))
        user_count = cursor.fetchone()[0] - 1
        return render_template("home.html", num_rec=user_count, user=session["username"])
    else:
        return redirect(url_for("sign_up"))

@app.route("/signup", methods=["POST", "GET"])
def sign_up():
    if 'username' in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        age = request.form.get("age")
        phone = request.form.get("phoneNumber")
        city = request.form.get("governorate")
        
        # Validate city
        try:
            city = int(city)
            if city < 1 or city > 27:
                return render_template("register.html", error_message="محافظة غير صحيحة")
        except ValueError:
            return render_template("register.html", error_message="محافظة غير صحيحة")

        # Validate other fields
        if not username or not password or not age or not phone or not city:
            return render_template("register.html", error_message="كل الحقول يجب ان تملاء")

        # Validate age
        try:
            if int(age) < 18:
                return render_template("register.html", error_message="السن اصغر من 18 سنة")
        except ValueError:
            return render_template("register.html", error_message="السن خطأ")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template("register.html", error_message="الاسم مسجل بالفعل")
        cursor.execute("SELECT * FROM user WHERE phone = ?", (phone,))
        tel = cursor.fetchone()
        if tel:
            return render_template("register.html", error_message="رقم الهاتف مسجل بالفعل")
        if len(phone) != 11 or phone[0] != "0" or phone[1] != "1" or phone[2] not in ["5", "1", "2", "0"]:
            return render_template("register.html", error_message="رقم الهاتف غير صحيح")

        # Insert user into the database
        try:
            cursor.execute('INSERT INTO user (username, password, age, phone, city) VALUES (?, ?, ?, ?, ?)', 
                           (username, password, age, phone, city))
            conn.commit()
            cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
            user_id = cursor.fetchone()["id"]
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error_message="اسم المستخدم موجود بالفعل")
        finally:
            conn.close()
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            session['user_id'] = user["id"]
            return redirect(url_for('home'))
        else:
            error_message = "اسم المستخدم أو كلمة المرور غير صحيحة"
            return render_template("login.html", error_message=error_message)
    
    return render_template("login.html")

@app.route('/air_quality', methods=['GET'])
def air_quality():
    if 'username' not in session:
        return redirect(url_for("home"))
    city = request.args.get('city', default='cairo', type=str)
    url = f"{BASE_URL}{city}/?token={API}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Assuming the data you need is in the 'data' key
        if data['status'] == 'ok':
            aqi = data['data']['aqi']
            components = data['data']['iaqi']
            pollution = components["pm25"]["v"]
            msg = ""
            if pollution < 12:
                msg = "جيد"
            elif pollution > 35.4 and pollution < 55:
                msg = "غير صحي للمريضين"
            elif pollution > 55.5 and pollution < 150.4:
                msg = "غير صحي"
            elif pollution > 150.5 and pollution < 250:
                msg = "غير صحي للغاية"
            else:
                msg = "سام"
            return render_template('air_quality.html', msg=msg, pollution=pollution, user=session["username"])
        else:
            return render_template("air_quality.html", user=session["username"])
    except requests.RequestException as e:
        return f"Error fetching data from API: {e}", 500

@app.route('/users', methods=['GET'])
def users():
    if 'username' not in session:
        return redirect(url_for("home"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT city FROM user WHERE username = ?", (session["username"],))
    city_row = cursor.fetchone()
    users = cursor.execute("SELECT * FROM user WHERE city = ? AND username != ?", (city_row[0], session["username"]))
    if users:
        return render_template("users.html", users=users, user=session["username"])
    else:
        return render_template("users.html", users="لا يوجد مستخدمين بمنطقطك", user=session["username"])

@app.route('/chat/<username>', methods=['GET'])
def chat(username):
    user = db.execute("SELECT username FROM user WHERE username = ?", (username,))
    if len(user) == 0:
        return redirect(url_for('home')) 
    session["reciever"] = username
    return render_template("chat.html", user=session["username"], name=username)

users = {}  # Global dictionary to store connected users

@socketio.on('connect')
def handle_connect():
    if "user_id" in session:
        username = db.execute("SELECT username FROM user WHERE id = ?", session["user_id"])[0]["username"]
        users[username] = request.sid
        if "reciever" in session:
            msgs = db.execute("SELECT msg, sender, timestamp FROM msgs WHERE (reciever = ? AND sender = ?) OR (reciever = ? AND sender = ?) ORDER BY timestamp", session["reciever"], username, username, session["reciever"])
            for msg in msgs:
                if msg['sender'] == username:
                    emit('message', {'msg': msg['msg'], 'timestamp': msg["timestamp"]}, room=users[username])
                else:
                    emit('message1', {'msg': msg['msg'], 'timestamp': msg["timestamp"]}, room=users[username])

@socketio.on('disconnect')
def handle_disconnect():
    if "username" in session:
        username = session["username"]
        if username in users:
            del users[username]
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    if "user_id" in session:
        reciever_id = db.execute("SELECT id FROM user WHERE username = ?", data['recipient'])[0]["id"]
        name = db.execute("SELECT username FROM user WHERE id = ?", session["user_id"])[0]["username"]
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        db.execute("INSERT INTO msgs (msg, reciever, reciever_id, sender, sender_id, timestamp) VALUES(?, ?, ?, ?, ?, ?)", data["msg"], data['recipient'], reciever_id, name, session["user_id"], now_str)
        if data["recipient"] in users:
            recipient_session_id = users[data['recipient']]
            emit('message', {'msg': data['msg'], 'timestamp': now_str}, room=recipient_session_id)

if __name__ == "__main__":
    socketio.run(app, debug=True)
