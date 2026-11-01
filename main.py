import cv2
import face_recognition
import numpy as np
import time
from database import get_all_users_with_encodings, log_access

print("--- DEMARRAGE DU SYSTEME DE CONTROLE D'ACCES ---")
print("Chargement des profils autorises depuis la base de donnees...")

# Récupération des enregistrements SQL (JOIN users & face_encodings)
db_records = get_all_users_with_encodings()

known_face_encodings = []
known_face_users = []

for record in db_records:
    user_id, nom, prenom, role, encoding_blob = record
    
    # Conversion du BLOB binaire en tableau numpy float64 (128 valeurs)
    encoding = np.frombuffer(encoding_blob, dtype=np.float64)
    
    known_face_encodings.append(encoding)
    known_face_users.append({
        "id": user_id,
        "nom": nom,
        "prenom": prenom,
        "role": role
    })

print(f"{len(known_face_encodings)} profil(s) autorise(s) charge(s) en memoire.")

cap = cv2.VideoCapture(0)

# Variables pour eviter la saturation des logs (mecanisme anti-spam)
last_log_time = 0
LOG_COOLDOWN = 4  # Enregistre un log toutes les 4 secondes maximum

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur de lecture du flux video.")
        break

    # Optimisation : Redimensionnement de la frame a 25% de sa taille d'origine
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

# Detection et calcul des empreintes sur l'image reduite
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    current_time = time.time()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Repositionnement des coordonnees du visage a l'echelle 1:1 (x4)
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        name = "INCONNU"
        role = "Non autorise"
        status = "DENIED"
        color = (0, 0, 255)  # Rouge pour DENIED
        user_id = None
        min_distance = 1.0

        if len(known_face_encodings) > 0:
            # Calcul de la distance euclidienne avec les visages connus
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            min_distance = distances[best_match_index]

            # Seuil d'acceptation biométrique (seuil standard = 0.50)
            if min_distance < 0.50:
                matched_user = known_face_users[best_match_index]
                user_id = matched_user["id"]
                name = f"{matched_user['prenom']} {matched_user['nom']}"
                role = matched_user["role"]
                status = "GRANTED"
                color = (0, 255, 0)  # Vert pour GRANTED

        # Insertion du log en BDD selon le cooldown
        if current_time - last_log_time > LOG_COOLDOWN:
            log_access(user_id=user_id, status=status, confidence_score=round(float(min_distance), 2))
            last_log_time = current_time
            print(f"[LOG ACCES] Statut: {status} | Nom: {name} | Distance: {min_distance:.2f}")

        # Dessin de l'interface visuelle sur le flux video
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        label = f"{name} | {status}"
        cv2.putText(frame, label, (left + 6, bottom - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

    cv2.imshow("Controle d'acces IT - Systeme en direct", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

