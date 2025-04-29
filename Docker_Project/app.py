from flask import Flask, request, redirect, render_template_string, session, url_for
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory user database
users = {}
# In-memory scores
scores = {}

# HTML Templates
login_page = """
<!doctype html>
<html lang="en">
<head>
    <title>Login - Catch Game</title>
</head>
<body style="background: linear-gradient(to right, #6a11cb, #2575fc); color: white; text-align:center;">
    <h1>Login</h1>
    <form method="post" action="/login">
        Username: <input name="username" required><br><br>
        Password: <input type="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
    <br>
    <p>Don't have an account? <a href="/signup" style="color:yellow;">Sign up</a></p>
</body>
</html>
"""

signup_page = """
<!doctype html>
<html lang="en">
<head>
    <title>Signup - Catch Game</title>
</head>
<body style="background: linear-gradient(to right, #11998e, #38ef7d); color: white; text-align:center;">
    <h1>Sign Up</h1>
    <form method="post" action="/signup">
        Username: <input name="username" required><br><br>
        Password: <input type="password" name="password" required><br><br>
        <button type="submit">Sign Up</button>
    </form>
    <br>
    <p>Already have an account? <a href="/" style="color:yellow;">Login</a></p>
</body>
</html>
"""

game_page = """
<!doctype html>
<html lang="en">
<head>
    <title>Catch Game</title>
    <style>
        canvas { background: linear-gradient(#1e3c72, #2a5298); display: block; margin: auto; }
        body { text-align: center; color: white; }
    </style>
</head>
<body>
    <h1>Catch the Stars!</h1>
    <p>Welcome, {{username}}! High Score: {{highscore}}</p>
    <canvas id="gameCanvas" width="400" height="600"></canvas>
    <p>Score: <span id="score">0</span></p>
    <button onclick="location.href='/leaderboard'">View Leaderboard</button>
    <button onclick="location.href='/logout'">Logout</button>
<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let basket = { x: 160, y: 550, width: 80, height: 20 };
let stars = [];
let score = 0;

document.addEventListener('mousemove', function(e) {
    basket.x = e.clientX - canvas.getBoundingClientRect().left - basket.width/2;
});

function createStar() {
    let x = Math.random() * 360;
    stars.push({x: x, y: 0});
}

function drawBasket() {
    ctx.fillStyle = 'yellow';
    ctx.fillRect(basket.x, basket.y, basket.width, basket.height);
}

function drawStars() {
    ctx.fillStyle = 'white';
    for (let star of stars) {
        ctx.beginPath();
        ctx.arc(star.x, star.y, 10, 0, Math.PI * 2);
        ctx.fill();
    }
}

function updateStars() {
    for (let star of stars) {
        star.y += 3;
    }
    stars = stars.filter(star => {
        if (star.y > 600) return false;
        if (star.x > basket.x && star.x < basket.x + basket.width && star.y > basket.y) {
            score++;
            document.getElementById('score').innerText = score;
            return false;
        }
        return true;
    });
}

function gameLoop() {
    ctx.clearRect(0, 0, 400, 600);
    drawBasket();
    drawStars();
    updateStars();
    requestAnimationFrame(gameLoop);
}

setInterval(createStar, 800);
gameLoop();

window.onbeforeunload = function() {
    fetch('/save_score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'score=' + score
    });
};
</script>
</body>
</html>
"""

leaderboard_page = """
<!doctype html>
<html lang="en">
<head>
    <title>Leaderboard - Catch Game</title>
</head>
<body style="background: linear-gradient(to right, #ff512f, #dd2476); color: white; text-align:center;">
    <h1>Leaderboard</h1>
    <table border="1" style="margin:auto; background:white; color:black;">
        <tr><th>Username</th><th>High Score</th></tr>
        {% for user, score in leaderboard %}
            <tr><td>{{user}}</td><td>{{score}}</td></tr>
        {% endfor %}
    </table>
    <br>
    <button onclick="location.href='/game'">Back to Game</button>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(login_page)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users[request.form['username']] = request.form['password']
        scores[request.form['username']] = 0
        return redirect(url_for('home'))
    return render_template_string(signup_page)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('game'))
    return 'Invalid credentials'

@app.route('/game')
def game():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template_string(game_page, username=session['username'], highscore=scores.get(session['username'], 0))

@app.route('/save_score', methods=['POST'])
def save_score():
    if 'username' in session:
        score = int(request.form['score'])
        if score > scores.get(session['username'], 0):
            scores[session['username']] = score
    return '', 204

@app.route('/leaderboard')
def leaderboard():
    board = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return render_template_string(leaderboard_page, leaderboard=board)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
