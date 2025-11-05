import os
from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
from models import db, Student, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from openpyxl import Workbook
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder=None)
    
    # Configuration CORS pour production
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "DELETE", "OPTIONS"])
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change_me')
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route('/api/apply', methods=['POST'])
    def apply():
        try:
            data = request.get_json(force=False) or {}
        except BadRequest:
            return jsonify({'error':'Invalid JSON payload'}), 400
        prenom = (data.get('prenom') or '').strip()
        nom = (data.get('nom') or '').strip()
        filiere = data.get('filiere')
        annee = data.get('annee')
        groupe = data.get('groupe')
        if not all([prenom, nom, filiere, annee, groupe]):
            return jsonify({'error': "Tous les champs sont requis"}), 400
        try:
            s = Student(prenom=prenom, nom=nom, filiere=filiere, annee=annee, groupe=groupe)
            db.session.add(s)
            db.session.commit()
            return jsonify({'message': 'Inscription enregistrée'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Vous avez déjà postulé avec ces informations'}), 409

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        data = request.get_json() or {}
        password = data.get('password', '')
        admin = Admin.query.filter_by(username='admin').first()
        if not admin or not check_password_hash(admin.password_hash, password):
            return jsonify({'error': 'Mot de passe invalide'}), 401
        return jsonify({'message': 'ok'}), 200

    @app.route('/api/admin/students', methods=['GET'])
    def list_students():
        filiere = request.args.get('filiere')
        annee = request.args.get('annee')
        groupe = request.args.get('groupe')
        q = Student.query
        if filiere: q = q.filter_by(filiere=filiere)
        if annee: q = q.filter_by(annee=annee)
        if groupe: q = q.filter_by(groupe=groupe)
        students = q.order_by(Student.id.desc()).all()
        result = [{'id':s.id, 'prenom':s.prenom, 'nom':s.nom, 'filiere':s.filiere, 'annee':s.annee, 'groupe':s.groupe} for s in students]
        return jsonify(result)

    @app.route('/api/admin/students/<int:sid>', methods=['DELETE'])
    def delete_student(sid):
        s = Student.query.get_or_404(sid)
        db.session.delete(s)
        db.session.commit()
        return jsonify({'message': 'supprimé'}), 200

    @app.route('/api/admin/export', methods=['GET'])
    def export_students():
        filiere = request.args.get('filiere')
        annee = request.args.get('annee')
        groupe = request.args.get('groupe')
        q = Student.query
        if filiere: q = q.filter_by(filiere=filiere)
        if annee: q = q.filter_by(annee=annee)
        if groupe: q = q.filter_by(groupe=groupe)
        students = q.all()

        wb = Workbook()
        ws = wb.active
        ws.append(['Prénom', 'Nom', 'Filière', 'Année', 'Groupe'])
        for s in students:
            ws.append([s.prenom, s.nom, s.filiere, s.annee, s.groupe])
        bio = BytesIO()
        wb.save(bio)
        bio.seek(0)
        return send_file(bio, download_name='students.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({'error': getattr(e, 'description', 'Bad Request')}), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'error': getattr(e, 'description', 'Not Found')}), 404

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
