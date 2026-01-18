from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

DB_FILE = "database.db"


# ----------------------------
# DATABASE SETUP
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            paid INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ----------------------------
# HOME PAGE – FORM
# ----------------------------
@app.route("/")
def home():
    return render_template("form.html")


# ----------------------------
# FORM SUBMIT
# ----------------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO members (name, email, phone, paid) VALUES (?, ?, ?, 0)",
        (name, email, phone)
    )
    conn.commit()
    member_id = cur.lastrowid
    conn.close()

    return redirect(url_for("payment", member_id=member_id))


# ----------------------------
# DEMO PAYMENT PAGE
# ----------------------------
@app.route("/payment/<int:member_id>")
def payment(member_id):
    return render_template("payment.html", member_id=member_id)


# ----------------------------
# PAYMENT SUCCESS
# ----------------------------
@app.route("/success/<int:member_id>")
def success(member_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE members SET paid = 1 WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

    return render_template("success.html", member_id=member_id)


# ----------------------------
# DOWNLOAD MEMBERSHIP CARD (PDF)
# ----------------------------
@app.route("/download/<int:member_id>")
def download(member_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT name, email, phone FROM members WHERE id=? AND paid=1",
        (member_id,)
    )
    member = cur.fetchone()
    conn.close()

    if not member:
        return "Payment not completed or member not found", 403

    name, email, phone = member

    pdf_name = f"membership_card_{member_id}.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=(595, 842))  # A4

    # ----------------------------
    # BACKGROUND
    # ----------------------------
    c.setFillColorRGB(0.95, 0.97, 1)
    c.rect(0, 0, 595, 842, fill=1)

    # ----------------------------
    # HEADER BANNER
    # ----------------------------
    c.setFillColorRGB(0.1, 0.4, 0.8)
    c.rect(0, 760, 595, 82, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(297, 795, "SOCIAL CARE MEMBERSHIP")

    c.setFont("Helvetica", 14)
    c.drawCentredString(297, 770, "Together We Serve Humanity")

    # ----------------------------
    # CARD BORDER
    # ----------------------------
    c.setStrokeColorRGB(0.1, 0.4, 0.8)
    c.setLineWidth(3)
    c.rect(40, 120, 515, 620)

    # ----------------------------
    # MEMBER DETAILS BOX
    # ----------------------------
    c.setFillColorRGB(1, 1, 1)
    c.rect(80, 500, 435, 200, fill=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 670, "MEMBER DETAILS")

    c.setFont("Helvetica", 14)
    c.drawString(100, 630, f"Member ID : {member_id}")
    c.drawString(100, 600, f"Name      : {name}")
    c.drawString(100, 570, f"Email     : {email}")
    c.drawString(100, 540, f"Phone     : {phone}")

    # ----------------------------
    # SOCIAL CAUSE SECTION
    # ----------------------------
    c.setFillColorRGB(0.9, 0.95, 0.9)
    c.rect(80, 320, 435, 140, fill=1)

    c.setFillColorRGB(0.1, 0.5, 0.1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 430, "OUR MISSION")

    c.setFont("Helvetica", 13)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(100, 400, "• Education for underprivileged children")
    c.drawString(100, 375, "• Care & support for handicapped individuals")
    c.drawString(100, 350, "• Empowering poor families & communities")

    # ----------------------------
    # FOOTER
    # ----------------------------
    c.setFillColorRGB(0.1, 0.4, 0.8)
    c.rect(0, 0, 595, 80, fill=1)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(
        297,
        45,
        "Thank you for being a part of social change ❤️"
    )

    # SAVE PDF
    c.save()

    return send_file(pdf_path, as_attachment=True)


# ----------------------------
# APP START
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

