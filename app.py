from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# Setup an in-memory dummy database for testing
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'supersecret123')")
    c.execute("INSERT INTO users (username, password) VALUES ('guest', 'guestpass')")
    conn.commit()
    return conn

db_conn = init_db()

@app.route('/')
def index():
    return '''
        <html>
            <head><title>Vulnerable App for ZAP Testing</title></head>
            <body>
                <h1>Vulnerable App for ZAP Testing</h1>
                <p>This is a deliberately vulnerable application designed to test OWASP ZAP scanning.</p>
                <ul>
                    <li><a href="/xss?name=Visitor">Test Reflected XSS</a></li>
                    <li><a href="/sqli?user=admin">Test SQL Injection</a></li>
                </ul>
            </body>
        </html>
    '''

@app.route('/xss')
def xss():
    # Vulnerability: Reflected Cross-Site Scripting (XSS)
    # The user input 'name' is directly rendered into the HTML template without sanitization.
    name = request.args.get('name', 'World')
    template = f"<h1>Hello {name}!</h1><p>Go <a href='/'>back</a></p>"
    return render_template_string(template)

@app.route('/sqli')
def sqli():
    # Vulnerability: SQL Injection (SQLi)
    # The user input 'user' is concatenated directly into the SQL query string.
    user = request.args.get('user', '')
    query = f"SELECT * FROM users WHERE username = '{user}'"
    try:
        c = db_conn.cursor()
        c.execute(query)
        result = c.fetchall()
        
        # Also returns raw errors if the query fails (Information Exposure)
        return f"<h3>Results for user: {user}</h3><p>{result}</p><p>Go <a href='/'>back</a></p>"
    except Exception as e:
        return f"<h3>Database Error:</h3><p>{e}</p><p>Go <a href='/'>back</a></p>"

if __name__ == '__main__':
    # Binding to 0.0.0.0 to allow access from outside the Docker container
    app.run(host='0.0.0.0', port=5000)
