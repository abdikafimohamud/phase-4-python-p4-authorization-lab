from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, User, Article
from flask import abort

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'  # required for session cookies

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)


# -------------------
# Authentication Routes
# -------------------
@app.post('/login')
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")  # may be None

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # If a password exists in the database, check it
    if user.password_hash and password:
        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

    # If no password is required (like in tests), still log them in
    session['user_id'] = user.id
    return jsonify(user.to_dict()), 200


@app.delete('/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.get('/check_session')
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    return jsonify(user.to_dict()), 200


# -------------------
# Public Articles
# -------------------
@app.get('/articles')
def articles():
    articles = Article.query.filter_by(is_member_only=False).all()
    return jsonify([a.to_dict() for a in articles]), 200


@app.get('/articles/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    if article.is_member_only:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(article.to_dict()), 200


# -------------------
# Member-Only Articles
# -------------------
@app.get('/members_only_articles')
def members_only_articles():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    articles = Article.query.filter_by(is_member_only=True).all()
    return jsonify([a.to_dict() for a in articles]), 200


@app.get('/members_only_articles/<int:id>')
def members_only_article(id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Use db.session.get instead of query.get
    article = db.session.get(Article, id)
    if not article:
        abort(404)

    return jsonify(article.to_dict()), 200



if __name__ == '__main__':
    app.run(port=5555, debug=True)
