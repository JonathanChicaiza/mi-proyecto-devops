import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template

app = Flask(__name__)

# Configuración por variables de entorno
APP_NAME = os.getenv("APP_NAME", "Mi Aplicación Flask")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "devops_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    """Establece conexión con la base de datos."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    """Crea la tabla e inserta 5 registros iniciales con reintentos."""
    retries = 10
    while retries > 0:
        try:
            print("Intentando conectar a la base de datos...")
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Crear tabla
            cur.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    precio NUMERIC(10, 2) NOT NULL,
                    stock INT NOT NULL
                );
            ''')
            
            # Verificar si está vacía
            cur.execute("SELECT COUNT(*) FROM productos;")
            if cur.fetchone()[0] == 0:
                productos_iniciales = [
                    ('Laptop Asus', 850.00, 10),
                    ('Mouse Logitech', 25.50, 50),
                    ('Teclado Mecánico', 65.00, 30),
                    ('Monitor 24" Dell', 180.00, 15),
                    ('Auriculares Sony', 90.00, 20)
                ]
                cur.executemany(
                    "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s);",
                    productos_iniciales
                )
                
            conn.commit()
            cur.close()
            conn.close()
            print("¡Base de datos inicializada correctamente!")
            return True
        except Exception as e:
            retries -= 1
            print(f"Postgres no está listo aún ({retries} reintentos restantes). Esperando 3 segundos...")
            time.sleep(3)
    return False

@app.route('/')
def index():
    status = "Conectado exitosamente"
    try:
        conn = get_db_connection()
        conn.close()
    except Exception as e:
        status = f"Error de conexión: {e}"

    return render_template('index.html', app_name=APP_NAME, version=APP_VERSION, status=status)

@app.route('/productos')
def productos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nombre, precio, stock FROM productos;")
        lista_productos = cur.fetchall()
        cur.close()
        conn.close()
        error = None
    except Exception as e:
        lista_productos = []
        error = f"No se pudieron cargar los productos: {e}"
        
    return render_template('productos.html', productos=lista_productos, error=error)

if __name__ == '__main__':
    # Aseguramos la inicialización antes de lanzar el servidor web
    init_db()
    # Arranca Flask en el puerto 5000
    app.run(host='0.0.0.0', port=5000)