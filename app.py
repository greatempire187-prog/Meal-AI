from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
import base64
from werkzeug.utils import secure_filename
import sqlite3
import re

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DATABASE = 'meal_planner.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create ingredients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT,
            prep_time INTEGER,
            cook_time INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create meal_plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id TEXT UNIQUE NOT NULL,
            day TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            meal_name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create grocery_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grocery_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sample meal database
MEAL_DATABASE = {
    'chicken': {
        'breakfast': [
            {'name': 'Chicken and Egg Scramble', 'ingredients': ['Chicken breast', 'Eggs', 'Bell peppers', 'Onions', 'Cheese'], 'prep_time': 15, 'cook_time': 10},
            {'name': 'Chicken Breakfast Burrito', 'ingredients': ['Chicken breast', 'Tortillas', 'Eggs', 'Potatoes', 'Salsa'], 'prep_time': 20, 'cook_time': 15}
        ],
        'lunch': [
            {'name': 'Grilled Chicken Salad', 'ingredients': ['Chicken breast', 'Lettuce', 'Tomatoes', 'Cucumber', 'Olive oil'], 'prep_time': 15, 'cook_time': 20},
            {'name': 'Chicken Stir Fry', 'ingredients': ['Chicken breast', 'Broccoli', 'Rice', 'Soy sauce', 'Garlic'], 'prep_time': 20, 'cook_time': 15}
        ],
        'dinner': [
            {'name': 'Baked Chicken with Vegetables', 'ingredients': ['Chicken breast', 'Potatoes', 'Carrots', 'Onions', 'Herbs'], 'prep_time': 15, 'cook_time': 45},
            {'name': 'Chicken Pasta', 'ingredients': ['Chicken breast', 'Pasta', 'Tomato sauce', 'Garlic', 'Parmesan'], 'prep_time': 10, 'cook_time': 25}
        ]
    },
    'beef': {
        'breakfast': [
            {'name': 'Beef and Hash Browns', 'ingredients': ['Ground beef', 'Potatoes', 'Onions', 'Eggs'], 'prep_time': 15, 'cook_time': 20}
        ],
        'lunch': [
            {'name': 'Beef Tacos', 'ingredients': ['Ground beef', 'Tortillas', 'Lettuce', 'Tomatoes', 'Cheese'], 'prep_time': 20, 'cook_time': 15},
            {'name': 'Beef Sandwich', 'ingredients': ['Ground beef', 'Bread', 'Lettuce', 'Tomatoes', 'Mayo'], 'prep_time': 10, 'cook_time': 15}
        ],
        'dinner': [
            {'name': 'Spaghetti Bolognese', 'ingredients': ['Ground beef', 'Pasta', 'Tomato sauce', 'Onions', 'Garlic'], 'prep_time': 15, 'cook_time': 30},
            {'name': 'Beef Stir Fry', 'ingredients': ['Ground beef', 'Broccoli', 'Rice', 'Soy sauce', 'Ginger'], 'prep_time': 20, 'cook_time': 15}
        ]
    },
    'fish': {
        'breakfast': [
            {'name': 'Smoked Salmon Bagel', 'ingredients': ['Salmon', 'Bagel', 'Cream cheese', 'Onions', 'Cap'], 'prep_time': 10}
        ],
        'lunch': [
            {'name': 'Grilled Salmon Salad', 'ingredients': ['Salmon', 'Lettuce', 'Avocado', 'Lemon', 'Olive oil'], 'prep_time': 15, 'cook_time': 20}
        ],
        'dinner': [
            {'name': 'Baked Salmon', 'ingredients': ['Salmon', 'Lemon', 'Dill', 'Olive oil', 'Asparagus'], 'prep_time': 10, 'cook_time': 25},
            {'name': 'Fish Tacos', 'ingredients': ['Salmon', 'Tortillas', 'Cabbage', 'Lime', 'Sour cream'], 'prep_time': 20, 'cook_time': 15}
        ]
    },
    'vegetarian': {
        'breakfast': [
            {'name': 'Oatmeal with Berries', 'ingredients': ['Oats', 'Milk', 'Berries', 'Honey', 'Nuts'], 'prep_time': 5, 'cook_time': 10},
            {'name': 'Avocado Toast', 'ingredients': ['Bread', 'Avocado', 'Lemon', 'Salt', 'Pepper'], 'prep_time': 5, 'cook_time': 5}
        ],
        'lunch': [
            {'name': 'Vegetable Stir Fry', 'ingredients': ['Broccoli', 'Carrots', 'Rice', 'Soy sauce', 'Garlic'], 'prep_time': 20, 'cook_time': 15},
            {'name': 'Caprese Salad', 'ingredients': ['Tomatoes', 'Mozzarella', 'Basil', 'Olive oil', 'Balsamic'], 'prep_time': 15}
        ],
        'dinner': [
            {'name': 'Pasta Primavera', 'ingredients': ['Pasta', 'Broccoli', 'Tomatoes', 'Garlic', 'Olive oil'], 'prep_time': 15, 'cook_time': 20},
            {'name': 'Vegetable Curry', 'ingredients': ['Coconut milk', 'Vegetables', 'Rice', 'Curry powder', 'Onions'], 'prep_time': 20, 'cook_time': 30}
        ]
    }
}

# Common pantry items
PANTRY_STAPLES = [
    {'name': 'Salt', 'category': 'spices', 'priority': 'high'},
    {'name': 'Pepper', 'category': 'spices', 'priority': 'high'},
    {'name': 'Olive oil', 'category': 'oils', 'priority': 'high'},
    {'name': 'Cooking oil', 'category': 'oils', 'priority': 'medium'},
    {'name': 'Butter', 'category': 'dairy', 'priority': 'medium'},
    {'name': 'Milk', 'category': 'dairy', 'priority': 'medium'},
    {'name': 'Eggs', 'category': 'dairy', 'priority': 'high'},
    {'name': 'Bread', 'category': 'bakery', 'priority': 'medium'},
    {'name': 'Flour', 'category': 'baking', 'priority': 'low'},
    {'name': 'Sugar', 'category': 'baking', 'priority': 'low'},
    {'name': 'Coffee', 'category': 'beverages', 'priority': 'medium'},
    {'name': 'Tea', 'category': 'beverages', 'priority': 'low'}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-receipt', methods=['POST'])
def process_receipt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Simulate OCR processing (in real implementation, use OCR library)
            extracted_items = simulate_ocr_processing(filepath)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'items': extracted_items
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({'error': 'No items provided'}), 400
        
        grocery_items = data['items']
        plan_id = str(uuid.uuid4())
        
        # Store grocery items in database
        store_grocery_items(plan_id, grocery_items)
        
        # Generate meal plan
        meal_plan = create_meal_plan(grocery_items)
        
        # Store meal plan in database
        store_meal_plan(plan_id, meal_plan)
        
        # Generate shopping list
        shopping_list = generate_shopping_list(grocery_items, meal_plan)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'meal_plan': meal_plan,
            'shopping_list': shopping_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-meal-plan', methods=['POST'])
def save_meal_plan():
    try:
        data = request.get_json()
        
        if not data or 'plan_id' not in data:
            return jsonify({'error': 'No plan ID provided'}), 400
        
        plan_id = data['plan_id']
        modifications = data.get('modifications', {})
        
        # Update meal plan in database
        update_meal_plan(plan_id, modifications)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simulate_ocr_processing(filepath):
    """Simulate OCR processing of receipt image"""
    # In a real implementation, you would use OCR libraries like:
    # - pytesseract
    # - google-cloud-vision
    # - azure-cognitiveservices-vision-computervision
    
    # For demo purposes, return sample items
    sample_receipts = [
        [
            {'name': 'Chicken breast', 'quantity': '2 lbs', 'category': 'protein'},
            {'name': 'Broccoli', 'quantity': '1 head', 'category': 'vegetable'},
            {'name': 'Rice', 'quantity': '2 lbs', 'category': 'grain'},
            {'name': 'Olive oil', 'quantity': '1 bottle', 'category': 'oil'},
            {'name': 'Garlic', 'quantity': '1 bulb', 'category': 'vegetable'},
            {'name': 'Lemons', 'quantity': '3 pieces', 'category': 'fruit'}
        ],
        [
            {'name': 'Ground beef', 'quantity': '1.5 lbs', 'category': 'protein'},
            {'name': 'Tomatoes', 'quantity': '4 pieces', 'category': 'vegetable'},
            {'name': 'Pasta', 'quantity': '1 box', 'category': 'grain'},
            {'name': 'Onions', 'quantity': '2 pieces', 'category': 'vegetable'},
            {'name': 'Basil', 'quantity': '1 bunch', 'category': 'herb'},
            {'name': 'Parmesan cheese', 'quantity': '1 block', 'category': 'dairy'}
        ],
        [
            {'name': 'Salmon fillets', 'quantity': '4 pieces', 'category': 'protein'},
            {'name': 'Asparagus', 'quantity': '1 bunch', 'category': 'vegetable'},
            {'name': 'Potatoes', 'quantity': '5 pieces', 'category': 'vegetable'},
            {'name': 'Butter', 'quantity': '1 stick', 'category': 'dairy'},
            {'name': 'Dill', 'quantity': '1 bunch', 'category': 'herb'},
            {'name': 'Lemon', 'quantity': '1 piece', 'category': 'fruit'}
        ]
    ]
    
    import random
    return random.choice(sample_receipts)

def create_meal_plan(grocery_items):
    """Create a 7-day meal plan based on available ingredients"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meal_types = ['breakfast', 'lunch', 'dinner']
    
    # Determine main protein type
    protein_type = 'vegetarian'
    for item in grocery_items:
        item_lower = item['name'].lower()
        if 'chicken' in item_lower:
            protein_type = 'chicken'
            break
        elif 'beef' in item_lower or 'ground' in item_lower:
            protein_type = 'beef'
            break
        elif 'salmon' in item_lower or 'fish' in item_lower:
            protein_type = 'fish'
            break
    
    meal_plan = {}
    
    for day in days:
        daily_meals = {}
        for meal_type in meal_types:
            available_meals = MEAL_DATABASE[protein_type].get(meal_type, MEAL_DATABASE['vegetarian'][meal_type])
            meal = available_meals[len(day) % len(available_meals)]
            daily_meals[meal_type] = meal
        meal_plan[day] = daily_meals
    
    return meal_plan

def generate_shopping_list(grocery_items, meal_plan):
    """Generate shopping list for missing pantry items"""
    shopping_list = []
    existing_items = [item['name'].lower() for item in grocery_items]
    
    for staple in PANTRY_STAPLES:
        if not any(staple['name'].lower() in item for item in existing_items):
            if staple['priority'] == 'high' or (staple['priority'] == 'medium' and len(shopping_list) < 8):
                shopping_list.append({
                    'name': staple['name'],
                    'category': staple['category'],
                    'reason': f'Common {staple["category"]} staple',
                    'priority': staple['priority']
                })
    
    return shopping_list[:10]  # Limit to 10 items

def store_grocery_items(plan_id, items):
    """Store grocery items in database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for item in items:
        cursor.execute('''
            INSERT INTO grocery_items (plan_id, item_name, quantity, category)
            VALUES (?, ?, ?, ?)
        ''', (plan_id, item['name'], item.get('quantity', ''), item.get('category', '')))
    
    conn.commit()
    conn.close()

def store_meal_plan(plan_id, meal_plan):
    """Store meal plan in database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for day, meals in meal_plan.items():
        for meal_type, meal_data in meals.items():
            cursor.execute('''
                INSERT INTO meal_plans (plan_id, day, meal_type, meal_name, ingredients)
                VALUES (?, ?, ?, ?, ?)
            ''', (plan_id, day, meal_type, meal_data['name'], json.dumps(meal_data['ingredients'])))
    
    conn.commit()
    conn.close()

def update_meal_plan(plan_id, modifications):
    """Update meal plan with user modifications"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for modification in modifications:
        day = modification.get('day')
        meal_type = modification.get('meal_type')
        new_meal = modification.get('new_meal')
        
        if day and meal_type and new_meal:
            cursor.execute('''
                UPDATE meal_plans 
                SET meal_name = ?, ingredients = ?
                WHERE plan_id = ? AND day = ? AND meal_type = ?
            ''', (new_meal['name'], json.dumps(new_meal['ingredients']), plan_id, day, meal_type))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
