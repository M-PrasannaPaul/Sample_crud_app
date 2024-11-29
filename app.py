from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import time

app = Flask(__name__)


db_user = os.getenv('DATABASE_USER', 'root')
db_password = os.getenv('DATABASE_PASSWORD', 'Paul*1928')
db_host = os.getenv('DATABASE_HOST', 'db')
db_name = os.getenv('DATABASE_DB', 'sample_crud_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('items', lazy=True))

# Waiting for the database to be ready
with app.app_context():
    while True:
        try:
            db.create_all()  # Create tables
            print("Database is ready!")
            break
        except Exception as e:
            print(f"Waiting for the database to be ready... Error: {e}")
            time.sleep(5)

# Routes
@app.route("/")
def home():
    items = Item.query.all()
    return render_template("home.html", items=items)

@app.route('/item', methods=['POST'])
def create_item():
    data = request.get_json()
    existing_item = Item.query.get(data['id'])
    if existing_item:
        return jsonify({'message': 'Item ID already exists!'}), 400

    new_item = Item(
        id=data['id'],
        name=data['name'],
        description=data.get('description', ''),
        category_id=data.get('category_id')
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item created!'}), 201

@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'category': item.category.name if item.category_id else None
    } for item in items])

@app.route('/item/<int:id>', methods=['GET'])
def get_item(id):
    item = Item.query.get_or_404(id)
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description})

@app.route('/item/<int:id>', methods=['PUT'])
def update_item(id):
    item = Item.query.get_or_404(id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    db.session.commit()
    return jsonify({'message': 'Item updated!'})

@app.route('/item/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
