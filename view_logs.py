import sqlite3


def display_logs():
  conn = sqlite3.connect("controle_acces.db")
  cursor = conn.cursor()

  cursor.execute("""
        SELECT access_logs.id, users.nom, users.prenom, access_logs.status, access_logs.confidence_score, access_logs.timestamp
        FROM access_logs
        LEFT JOIN users ON access_logs.user_id = users.id
        ORDER BY access_logs.timestamp DESC
    """)

  logs = cursor.fetchall()
  conn.close()

  print("\n=== HISTORIQUE DES ACCES (TABLE ACCESS_LOGS) ===")
  print(
      f"{'ID':<5} | {'Nom Complet':<25} | {'Statut':<10} | {'Distance':<10} |"
      " {'Horodatage'}"
  )
  print("-" * 75)

  for log in logs:
    log_id, nom, prenom, status, distance, timestamp = log
    full_name = f"{prenom} {nom}" if nom else "INCONNU / NON AUTORISE"
    print(
        f"{log_id:<5} | {full_name:<25} | {status:<10} | {distance:<10} |"
        f" {timestamp}"
    )


if __name__ == "__main__":
  display_logs()