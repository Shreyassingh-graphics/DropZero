from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import pymysql
from pymysql import Error
from flask_bcrypt import Bcrypt
from datetime import datetime
import csv
import io
import requests

app = Flask(__name__)
app.secret_key = "3f1a8e6b9c0d2f5a7e1d44abefc23998b7d4e61f2a0cd8ef3c3b7e22a9a5f6d9"   # change this in production
bcrypt = Bcrypt(app)

# ------------------ DATABASE CONNECTION ------------------ #
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="DropZero",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# ------------------ HOME / LOGIN ------------------ #
from flask import render_template, request, redirect, url_for, session, flash

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role", "user")  # Get role from form, default to user

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please try again.", "danger")
            return render_template("login.html")

        cursor = conn.cursor()

        try:
            if role == "admin":
                # Check admin table
                cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
                admin_account = cursor.fetchone()

                if admin_account and bcrypt.check_password_hash(admin_account["password_hash"], password):
                    session["admin_id"] = admin_account["admin_id"]
                    flash("Welcome Admin!", "success")
                    return redirect(url_for("admin_dashboard"))
            else:
                # Check users table
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_account = cursor.fetchone()

                if user_account and bcrypt.check_password_hash(user_account["password_hash"], password):
                    session["user_id"] = user_account["user_id"]
                    flash("Welcome User!", "success")
                    return redirect(url_for("user_dashboard"))

            flash("Invalid email or password", "danger")
        except Error as e:
            flash("An error occurred during login. Please try again.", "danger")
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")


# ------------------ REGISTER ------------------ #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please try again.", "danger")
            return render_template("register.html")
            
        cursor = conn.cursor()

        try:
            # check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered!", "warning")
                return redirect(url_for("register"))

            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            created_at = datetime.now()

            cursor.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, created_at),
            )
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
            
        except Error as e:
            flash("An error occurred during registration. Please try again.", "danger")
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# ------------------ DASHBOARDS ------------------ #
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        flash("Please log in as user first", "warning")
        return redirect(url_for("login"))
    return render_template("user_dashboard.html")

# ------------------ ADMIN FEATURES ------------------ #

@app.route("/admin/monitor_users", methods=["GET", "POST"])
def monitor_users():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        user_id = request.form.get("user_id")
        if user_id:
            conn = get_db_connection()
            if not conn:
                flash("Database connection failed. Please try again.", "danger")
                return redirect(url_for("admin_dashboard"))
                
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
                flash("User deleted successfully!", "success")
            except Error as e:
                flash("An error occurred while deleting user. Please try again.", "danger")
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for("admin_dashboard"))

    # GET request - return JSON for AJAX
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, name, email, created_at FROM users")
        users = cursor.fetchall()
        return jsonify(users)
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/admin/view_users")
def view_users():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please try again.", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, name, email, created_at FROM users")
        users = cursor.fetchall()
        return render_template("view_users.html", users=users)
    except Error as e:
        flash("An error occurred while fetching users. Please try again.", "danger")
        print(f"Database error: {e}")
        return redirect(url_for("admin_dashboard"))
    finally:
        cursor.close()
        conn.close()

@app.route("/admin/add_discussion", methods=["POST"])
def add_discussion():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    if "csv_file" not in request.files:
        flash("No file uploaded", "danger")
        return redirect(url_for("admin_dashboard"))

    file = request.files["csv_file"]
    if file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("admin_dashboard"))

    if file and file.filename.endswith(".csv"):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.reader(stream)

            conn = get_db_connection()
            if not conn:
                flash("Database connection failed. Please try again.", "danger")
                return redirect(url_for("admin_dashboard"))
                
            cursor = conn.cursor()

            # Skip header row
            next(csv_reader, None)

            for row in csv_reader:
                if len(row) >= 3:
                    username, comment, discussion_topic = row[0], row[1], row[2]
                    cursor.execute(
                        "INSERT INTO comment (username, comment, discussion_topic) VALUES (%s, %s, %s)",
                        (username, comment, discussion_topic)
                    )

            conn.commit()
            flash("Discussion data uploaded successfully!", "success")
        except Error as e:
            flash("An error occurred while uploading data. Please try again.", "danger")
            print(f"Database error: {e}")
        except Exception as e:
            flash("An error occurred while processing the file. Please check the file format.", "danger")
            print(f"File processing error: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    else:
        flash("Invalid file format. Please upload a CSV file.", "danger")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/generate_summary", methods=["POST"])
def generate_summary():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    # TODO: Integrate sentiments.py and summary.py here
    # For now, just a placeholder
    flash("Summary generation feature will be implemented once sentiments.py and summary.py are provided.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route('/generate_sentiment', methods=['POST'])
def generate_sentiment():
    if "admin_id" not in session:
        flash("Access denied!", "danger")
        return redirect(url_for("login"))

    # Define the API endpoint URL
 # In app.py
    api_url = "https://743f20591f86.ngrok-free.app/analyze"
    try:
        # Make a POST request to the sentiment analysis API
        response = requests.post(api_url, timeout=60) # timeout of 5 seconds

        # Check if the API call was accepted
        if response.status_code == 200:
            flash("Sentiment analysis has been successfully started! The results will be available shortly.", "success")
        else:
            # Handle cases where the API might be down or returned an error
            flash(f"Failed to start sentiment analysis. API returned status: {response.status_code}", "danger")
            print(f"API Error: {response.text}")

    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., the API server is not running)
        flash("Could not connect to the sentiment analysis service. Please ensure it is running.", "danger")
        print(f"Connection Error: {e}")

    # Redirect back to the dashboard immediately
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/get_word_cloud")
def get_word_cloud():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    # TODO: Implement word cloud generation from summaries
    # For now, just a placeholder
    flash("Word cloud generation feature will be implemented.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/view_summary")
def view_summary():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    # TODO: Implement summary viewing functionality
    # For now, just a placeholder
    flash("Summary viewing feature will be implemented.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route('/view_sentiment_score')
def view_sentiment_score():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM sentiment_score ORDER BY sentiment_score DESC")
        results = cursor.fetchall()
    except Error as e:
        flash("Error fetching sentiment results", "danger")
        print("Database error:", e)
        results = []
    finally:
        cursor.close()
        conn.close()

    return render_template("view_sentiment_score.html", results=results)


@app.route("/admin/view_comments")
def view_comments():
    if "admin_id" not in session:
        flash("Please log in as admin first", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed. Please try again.", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor = conn.cursor()
    try:
        # Get all comments grouped by discussion topic
        cursor.execute("""
            SELECT discussion_topic, 
                   COUNT(*) as comment_count,
                   GROUP_CONCAT(CONCAT(username, ': ', comment) SEPARATOR '|||') as comments
            FROM comment 
            GROUP BY discussion_topic 
            ORDER BY discussion_topic
        """)
        topics_data = cursor.fetchall()
        
        # Process the data for better display
        processed_topics = []
        for topic in topics_data:
            comments_list = []
            if topic['comments']:
                comments = topic['comments'].split('|||')
                for comment in comments:
                    if ':' in comment:
                        username, comment_text = comment.split(':', 1)
                        comments_list.append({
                            'username': username.strip(),
                            'comment': comment_text.strip()
                        })
            
            processed_topics.append({
                'topic': topic['discussion_topic'],
                'comment_count': topic['comment_count'],
                'comments': comments_list
            })
        
        return render_template("view_comments.html", topics=processed_topics)
        
    except Error as e:
        flash("An error occurred while fetching comments. Please try again.", "danger")
        print(f"Database error: {e}")
        return redirect(url_for("admin_dashboard"))
    finally:
        cursor.close()
        conn.close()

# ------------------ LOGOUT ------------------ #
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
