import sqlite3


def init_db():
  conn = sqlite3.connect('controle_acces.db')
  cursor = conn.cursor()

  # Creation de la table users
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

  # Creation de la table face_encodings
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_encodings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        encoding_data BLOB NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

  # Creation de la table access_logs
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        confidence_score REAL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    )
    ''')

  conn.commit()
  conn.close()
  print('La base de donnees controle_acces.db a ete creee avec succes !')


if __name__ == '__main__':
  init_db()

def add_user(nom, prenom, role):
  conn = sqlite3.connect("controle_acces.db")
  cursor = conn.cursor()

  cursor.execute(
      "INSERT INTO users (nom, prenom, role) VALUES (?, ?, ?)",
      (nom, prenom, role),
  )

  user_id = cursor.lastrowid
  conn.commit()
  conn.close()

  return user_id

def add_face_encoding(user_id, encoding_data):
  conn = sqlite3.connect("controle_acces.db")
  cursor = conn.cursor()

  cursor.execute(
      "INSERT INTO face_encodings (user_id, encoding_data) VALUES (?, ?)",
      (user_id, encoding_data),
  )

  conn.commit()
  conn.close()

def log_access(user_id, status, confidence_score):
  conn = sqlite3.connect("controle_acces.db")
  cursor = conn.cursor()

  cursor.execute(
      "INSERT INTO access_logs (user_id, status, confidence_score) VALUES (?,"
      " ?, ?)",
      (user_id, status, confidence_score),
  )

  conn.commit()
  conn.close()

def get_all_users_with_encodings():
  conn = sqlite3.connect("controle_acces.db")
  cursor = conn.cursor()

  cursor.execute("""
    SELECT users.id, users.nom, users.prenom, users.role, face_encodings.encoding_data 
    FROM users 
    JOIN face_encodings ON users.id = face_encodings.user_id
    """)

  rows = cursor.fetchall()
  conn.close()

  return rows