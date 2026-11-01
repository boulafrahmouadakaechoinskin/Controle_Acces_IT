import cv2
import face_recognition
from database import add_face_encoding, add_user

print("=== ENREGISTREMENT D'UN NOUVEL UTILISATEUR ===")
nom = input("Entrez le Nom : ")
prenom = input("Entrez le Prenom : ")
role = input("Entrez le Role (ex: Technicien IT) : ")

cap = cv2.VideoCapture(0)
print(
    "\nPositionnez le visage devant la camera et appuyez sur 'c' pour"
    " Capturer la photo."
)

captured_frame = None

while True:
  ret, frame = cap.read()
  if not ret:
    print("Erreur de lecture de la camera.")
    break

  # Affichage des instructions sur la video
  cv2.putText(
      frame,
      "Appuyez sur 'c' pour Capturer",
      (20, 40),
      cv2.FONT_HERSHEY_SIMPLEX,
      0.7,
      (255, 255, 0),
      2,
  )
  cv2.imshow("Enregistrement Utilisateur - Capture", frame)

  key = cv2.waitKey(1) & 0xFF
  if key == ord("c"):
    captured_frame = frame.copy()
    print("Photo capturee avec succes !")
    break
  elif key == ord("q"):
    print("Annulation de l'enregistrement.")
    break

cap.release()
cv2.destroyAllWindows()

if captured_frame is not None:
  # Conversion BGR vers RGB (exige par face_recognition)
  rgb_frame = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)

  # Detection des visages
  face_locations = face_recognition.face_locations(rgb_frame)

  if len(face_locations) == 0:
    print(
        "Erreur : Aucun visage n'a ete detecte sur la photo. Recommencez"
        " l'operation."
    )
  else:
    # Calcul du vecteur d'encodage (128 valeurs numériques)
    encodings = face_recognition.face_encodings(
        rgb_frame, known_face_locations=face_locations
    )
    encoding_data = encodings[0].tobytes()

    # Sauvegarde dans la base de données
    user_id = add_user(nom, prenom, role)
    add_face_encoding(user_id, encoding_data)

    print(
        f"\nSucces : {prenom} {nom} ({role}) enregistre(e) avec l'ID"
        f" #{user_id} !"
    )