from datetime import timedelta
import os
from flask import Blueprint, render_template, request, jsonify
from flask_mail import Message
from app.auth.models import User, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token ,decode_token   
from flask_mail import Message
from app import mail

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['first_name', 'last_name', 'email', 'phone', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Le champ {field} est requis'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email déjà utilisé"}), 409

    user = User(
        first_name=data['first_name'].strip().title(),
        last_name=data['last_name'].strip().upper(),
        email=data['email'].strip().lower(),
        phone=data['phone'].strip()
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    confirm_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    confirm_url = f"http://localhost:5000/auth/confirm/{confirm_token}"

    msg = Message("🎉 Confirme ton compte Track & Find", recipients=[user.email])
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2c3e50;">Salut {user.first_name} {user.last_name},</h2>
        <p>Bienvenue sur <strong>Track & Find</strong> 🚀</p>
        <p>Pour confirmer ton compte et accéder à nos services :</p>

        <p style="text-align: center;">
            <a href="{confirm_url}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">
                Confirmer mon compte
            </a>
        </p>

        <p>Ce lien est valable <strong>24 heures</strong>. Passé ce délai, tu devras refaire la procédure d’inscription.</p>

        <p style="font-size: 0.9em; color: #999;">
            Si tu n’es pas à l’origine de cette demande, ignore simplement ce message.
        </p>

        <hr>
        <p style="font-size: 0.9em;">💡 Track & Find – Retrouvons ce qui compte.</p>
    </body>
    </html>
    """

    mail.send(msg)

    return jsonify({"message": "Inscription réussie. Un e-mail de confirmation t’a été envoyé."}), 201


@auth_bp.route('/login', methods=['POST'])

def login():
    """
    Login user and return access/refresh tokens
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
                user:
                  type: object
                  properties:
                    id: { type: string }
                    name: { type: string }
                    email: { type: string }
                    phone: { type: string }
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "email": user.email
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "email": user.email
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  
def refresh_access_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({
        "access_token": new_access_token
    })

@auth_bp.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']
        user = User.query.get(user_id)
        if not user:
            return "Utilisateur introuvable", 404
        if user.is_confirmed:
            print("✅ Utilisateur déjà confirmé")
            return render_template("confirm_error.html")  
        user.is_confirmed = True
        db.session.commit()

        return render_template("confirm_success.html")  

    except Exception as e:
        print("❌ Confirmation failed:", e)
        return render_template("confirm_error.html")
    

@auth_bp.route('/test-template')
def test_template():
    print("Dossier courant :", os.getcwd())
    print("confirm_success.html existe ?", os.path.exists("templates/confirm_success.html"))
    return render_template("confirm_success.html")
