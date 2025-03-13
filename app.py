import os
import requests
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ✅ API URL (vérifie que l'URL est correcte)
API_URL_BUY = "https://anti-refund-api.onrender.com/buy"
API_URL_REFUND = "https://anti-refund-api.onrender.com/refund"

# ✅ Connexion SQLite pour stocker les commandes localement (optionnel)
DB_PATH = "site1.db"

def init_db():
    """Créer la base de données SQLite locale"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()  # ✅ Initialiser la base de données

@app.route("/")
def index():
    """Afficher les produits et l'historique des achats"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()
    conn.close()

    products = [
        {"name": "iPhone 14 Pro", "price": 1299},
        {"name": "MacBook Air M2", "price": 1499},
        {"name": "iPad Pro", "price": 1099},
        {"name": "PlayStation 5", "price": 499}
    ]
    return render_template("index.html", products=products, orders=orders)

@app.route("/buy", methods=["POST"])
def buy():
    """Envoyer un achat à l'API et l'enregistrer localement"""
    product_name = request.form.get("product_name")
    payment_method = request.form.get("payment_method")

    data = {
        "product_name": product_name,
        "payment_method": payment_method
    }

    print("📤 Envoi des données à l'API:", data)  # ✅ Log pour debug

    try:
        response = requests.post(API_URL_BUY, json=data)
        response_json = response.json()
        print("✅ Réponse de l'API:", response_json)  # ✅ Vérification API
    except Exception as e:
        print("❌ Erreur lors de l'envoi à l'API:", e)
        return redirect("/")

    # ✅ Enregistrer l'achat localement
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (product_name, payment_method) VALUES (?, ?)", (product_name, payment_method))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/refund/<int:order_id>")
def refund(order_id):
    """Demander un remboursement"""
    try:
        response = requests.get(f"{API_URL_REFUND}/{order_id}")
        print("✅ Réponse API remboursement:", response.json())
    except Exception as e:
        print("❌ Erreur API remboursement:", e)

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

