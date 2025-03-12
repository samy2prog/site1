import os
import psycopg2
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ✅ URL de l'API de détection de fraude sur Render
API_URL = "https://anti-refund-api.onrender.com/detect"

# ✅ Connexion PostgreSQL (Render Internal Database URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eshop_user:Idx7b2u8UfXodOCQn3oGHwrzwtyP3CbI@dpg-cv908nin91rc73d5bes0-a/eshop_db_c764")

# ✅ Fonction pour se connecter à PostgreSQL
def get_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print("❌ ERREUR DE CONNEXION À POSTGRESQL :", e)
        return None

# ✅ Création des tables si elles n'existent pas
def create_tables():
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                product_name TEXT NOT NULL,
                ip TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                risk_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        cursor.close()
        db.close()
        print("✅ Tables créées avec succès.")

# ✅ Route pour afficher la boutique
@app.route("/")
def index():
    products = [
        {"name": "Sac Louis Vuitton", "price": 1500},
        {"name": "Montre Rolex", "price": 10000},
        {"name": "Chaussures Gucci", "price": 800}
    ]
    return render_template("index.html", products=products)

# ✅ Route pour traiter les achats
@app.route("/buy", methods=["POST"])
def buy():
    product_name = request.form.get("product_name")
    payment_method = request.form.get("payment_method")
    user_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    # Envoyer les infos à l'API de détection de fraude
    fraud_data = {
        "ip": user_ip,
        "user_agent": user_agent,
        "payment_method": payment_method,
        "refund_count": 0  # À récupérer dynamiquement si possible
    }
    
    try:
        response = requests.post(API_URL, json=fraud_data)
        risk_score = response.json().get("risk_score", 0)
    except Exception as e:
        print("❌ Erreur API :", e)
        risk_score = "Erreur API"

    # Enregistrer la commande en base de données
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO orders (product_name, ip, user_agent, payment_method, risk_score)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_name, user_ip, user_agent, payment_method, risk_score))
        db.commit()
        cursor.close()
        db.close()

    return render_template("confirmation.html", product_name=product_name, risk_score=risk_score)

# ✅ Route pour afficher l'historique des commandes
@app.route("/orders")
def orders():
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT id, product_name, ip, user_agent, payment_method, risk_score, created_at FROM orders ORDER BY created_at DESC")
        orders = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("orders.html", orders=orders)
    else:
        return "❌ Impossible de se connecter à la base de données."

# ✅ Lancer l'application
if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)
