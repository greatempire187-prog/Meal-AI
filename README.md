# Receipt to Meal Planner

An AI-powered web application that transforms grocery receipts into personalized meal plans.

## Features

- **Receipt Upload**: Upload receipt images for automatic OCR processing
- **Manual Entry**: Manually enter grocery items as an alternative
- **Smart Meal Planning**: AI generates 7-day meal plans based on available ingredients
- **Shopping Lists**: Suggests additional pantry staples you might need
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Backend Integration**: Full Flask backend with SQLite database

## Technology Stack

### Frontend
- HTML5
- CSS3 with modern animations
- Vanilla JavaScript (ES6+)
- Responsive design with mobile-first approach

### Backend
- Python 3.8+
- Flask web framework
- SQLite database
- Flask-CORS for API communication

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**:
   ```bash
   python app.py
   ```

5. **Open the application**:
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Or open `index.html` directly in your browser (for frontend-only mode)

## Usage

### Method 1: Receipt Upload
1. Click "Choose File" or drag and drop a receipt image
2. Wait for OCR processing to complete
3. Review extracted grocery items
4. Click "Generate Meal Plan"

### Method 2: Manual Entry
1. Check "Enter items manually instead"
2. Add grocery items with quantities
3. Click "Generate Meal Plan"

### Generated Results
- **7-Day Meal Plan**: Breakfast, lunch, and dinner for each day
- **Shopping List**: Additional pantry items you might need
- **Ingredient Breakdown**: Full list of required ingredients for each meal

## API Endpoints

### POST /api/process-receipt
Upload and process receipt images.

**Request**: `multipart/form-data`
- `file`: Image file (jpg, png, gif, webp)

**Response**:
```json
{
  "success": true,
  "items": [
    {
      "name": "Chicken breast",
      "quantity": "2 lbs",
      "category": "protein"
    }
  ]
}
```

### POST /api/generate-meal-plan
Generate meal plan from grocery items.

**Request**: `application/json`
```json
{
  "items": [
    {
      "name": "Chicken breast",
      "quantity": "2 lbs"
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "plan_id": "uuid-string",
  "meal_plan": {
    "Monday": {
      "breakfast": {
        "name": "Oatmeal with Berries",
        "ingredients": ["Oats", "Milk", "Berries"]
      }
    }
  },
  "shopping_list": [
    {
      "name": "Salt",
      "category": "spices",
      "reason": "Common pantry staple",
      "priority": "high"
    }
  ]
}
```

## Database Schema

The application uses SQLite with the following tables:

- **ingredients**: Stores ingredient information
- **meals**: Stores meal recipes and instructions
- **meal_plans**: Stores generated meal plans
- **grocery_items**: Stores user's grocery items

## File Structure

```
├── app.py              # Flask backend server
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── uploads/           # Temporary file uploads
└── meal_planner.db    # SQLite database
```

## Future Enhancements

- **Real OCR Integration**: Connect to actual OCR services (Google Vision, Azure, etc.)
- **User Accounts**: Add user authentication and saved meal plans
- **Recipe Details**: Full recipes with cooking instructions and nutritional info
- **Dietary Preferences**: Support for vegetarian, vegan, gluten-free, etc.
- **Shopping Integration**: Connect to grocery delivery services
- **Meal Customization**: Allow users to modify generated meals

## Troubleshooting

### Common Issues

1. **Server won't start**: Make sure port 5000 is not in use
2. **CORS errors**: Ensure Flask-CORS is properly installed
3. **Database errors**: Delete `meal_planner.db` and restart the server
4. **File upload issues**: Check file size (max 16MB) and format

### Development Mode

For development with hot reload:
```bash
export FLASK_ENV=development
python app.py
```

## License

This project is for educational purposes. Feel free to modify and distribute.

## Support

For issues and questions, please refer to the code comments or create an issue in the project repository.
