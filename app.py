import os
import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ✅ Connexion PostgreSQL (Render Internal Database URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eshop_user:Idx7b2u8UfXodOCQn3oGHwrzwtyP3CbI@dpg-cv908nin91rc73d5bes0-a/eshop_db_c764")

# ✅ Fonction pour se connecter à PostgreSQL
def get_db():
    """Connexion à PostgreSQL"""
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
                refund_requested BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.commit()
        cursor.close()
        db.close()
        print("✅ Tables créées avec succès.")

# ✅ Route pour afficher la boutique avec des produits électroniques
@app.route("/")
def index():
    products = [
        {"name": "iPhone 14 Pro", "price": 1299, "image": "https://cdn.pixabay.com/photo/2022/09/14/14/20/iphone-14-7454698_1280.jpg"},
        {"name": "iPad Pro", "price": 1099, "image": "https://cdn.pixabay.com/photo/2016/11/29/02/59/ipad-1868648_1280.png"},
        {"name": "MacBook Air M2", "price": 1499, "image": "https://cdn.pixabay.com/photo/2015/12/07/10/55/macbook-1081846_1280.jpg"},
        {"name": "PlayStation 5", "price": 599, "image": "https://cdn.pixabay.com/photo/2020/11/12/16/24/ps5-5734463_1280.jpg"}
    ]
    return render_template("index.html", products=products)

# ✅ Route pour traiter les achats et enregistrer la commande
@app.route("/buy", methods=["POST"])
def buy():
    product_name = request.form.get("product_name")
    payment_method = request.form.get("payment_method")
    user_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    # Enregistrer la commande en base de données
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO orders (product_name, ip, user_agent, payment_method)
            VALUES (%s, %s, %s, %s)
        """, (product_name, user_ip, user_agent, payment_method))
        db.commit()
        cursor.close()
        db.close()

    return redirect("/orders")

# ✅ Route pour afficher l'historique des commandes
@app.route("/orders")
def orders():
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT id, product_name, ip, user_agent, payment_method, refund_requested, created_at FROM orders ORDER BY created_at DESC")
        orders = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("orders.html", orders=orders)
    else:
        return "❌ Impossible de se connecter à la base de données."

# ✅ Route pour demander un remboursement et afficher une confirmation
@app.route("/refund/<int:order_id>")
def request_refund(order_id):
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("UPDATE orders SET refund_requested = TRUE WHERE id = %s", (order_id,))
        db.commit()
        cursor.close()
        db.close()
    return render_template("refund.html")

# ✅ Lancer l'application avec le port Render
if __name__ == "__main__":
    create_tables()
    port = int(os.environ.get("PORT", 10000))  # Utilise le port attribué par Render
    app.run(host="0.0.0.0", port=port, debug=True)
