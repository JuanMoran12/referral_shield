# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import csv, os

app = FastAPI()

DB_FILE = "referrals.csv"
MAX_REFERRALS_PER_USER = 10

# Si no existe el archivo, se crea con encabezados
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["referrer_email", "referee_email"])


class ReferralRequest(BaseModel):
    referrer_email: EmailStr
    referee_email: EmailStr


@app.get("/")
def read_root():  #Punto de entrada para verificar que la API está funcionando
    return {"message": "API de Referrals funcionando correctamente."}


@app.post("/referral")
def handle_referral(data: ReferralRequest):
    # Normalizar emails al inicio para todas las validaciones
    referrer = normalize_email(data.referrer_email)
    referee = normalize_email(data.referee_email)

    # --- Validaciones antifraude básicas ---
    # Comparar emails normalizados para evitar bypass con alias
    if referrer == referee:
        raise HTTPException(
            status_code=400,
            detail="Fraude: el referido no puede ser el mismo referidor.")

    # Verificar límite de referrals por persona (usando email normalizado)
    referral_count = count_referrals(referrer)
    if referral_count >= MAX_REFERRALS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=
            f"Fraude: el referidor ha excedido el límite de {MAX_REFERRALS_PER_USER} referencias."
        )

    if not validate_email_pattern(referee):
        raise HTTPException(
            status_code=400,
            detail="Fraude: el email del referido parece inválido o sospechoso."
        )

    if email_exists(referee):
        raise HTTPException(status_code=400,
                            detail="Fraude: el referido ya está registrado.")

    # --- Registrar en CSV (base simulada) ---
    with open(DB_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([referrer, referee])

    # --- Enviar email simulado ---
    print(f"✅ Enviando email de bienvenida a {referee}...")
    print(f"📧 Notificando agradecimiento a {referrer}...")

    return {"message": "Referido registrado exitosamente."}


def email_exists(email: str) -> bool:
    """Verifica si un correo ya está registrado en el CSV (usando normalización)"""
    normalized_email = normalize_email(email)
    with open(DB_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if normalize_email(row["referee_email"]) == normalized_email:
                return True
    return False


def validate_email_pattern(email: str) -> bool:
    """Chequeos simples para detectar correos sospechosos."""
    suspicious_patterns = [
        "test@", "fake@", "temp@", "mailinator", "example.com"
    ]
    return not any(pat in email for pat in suspicious_patterns)


def normalize_email(email: str) -> str:
    """
    Normaliza emails para evitar bypass con alias (+) y puntos en Gmail.
    Ejemplos:
    - user+1@gmail.com -> user@gmail.com
    - u.ser@gmail.com -> user@gmail.com
    - user+test@other.com -> user@other.com
    """
    email = email.lower().strip()

    if '@' not in email:
        return email

    username, domain = email.split('@', 1)

    # Remover todo después del signo +
    if '+' in username:
        username = username.split('+')[0]

    # Para Gmail/Googlemail, remover puntos del username
    if domain in ['gmail.com', 'googlemail.com']:
        username = username.replace('.', '')

    return f"{username}@{domain}"


def count_referrals(referrer_email: str) -> int:
    """Cuenta cuántos referrals ha hecho un referrer (usando normalización)."""
    normalized_referrer = normalize_email(referrer_email)
    count = 0
    with open(DB_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if normalize_email(row["referrer_email"]) == normalized_referrer:
                count += 1
    return count
