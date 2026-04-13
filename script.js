// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const manualEntrySection = document.getElementById('manualEntrySection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const uploadArea = document.getElementById('uploadArea');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const manualEntryCheckbox = document.getElementById('manualEntry');
const itemInput = document.getElementById('itemInput');
const quantityInput = document.getElementById('quantityInput');
const addItemBtn = document.getElementById('addItemBtn');
const generatePlanBtn = document.getElementById('generatePlanBtn');
const itemsContainer = document.getElementById('itemsContainer');
const newPlanBtn = document.getElementById('newPlanBtn');

// State Management
let groceryItems = [];
let currentMode = 'upload'; // 'upload' or 'manual'

// Event Listeners
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
manualEntryCheckbox.addEventListener('change', toggleManualEntry);
addItemBtn.addEventListener('click', addManualItem);
generatePlanBtn.addEventListener('click', generateMealPlan);
newPlanBtn.addEventListener('click', resetToStart);

// Keyboard shortcuts
itemInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addManualItem();
});
quantityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addManualItem();
});

// File Handling Functions
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processReceiptImage(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processReceiptImage(files[0]);
    }
}

// Toggle between upload and manual entry
function toggleManualEntry() {
    if (manualEntryCheckbox.checked) {
        uploadSection.classList.add('hidden');
        manualEntrySection.classList.remove('hidden');
        currentMode = 'manual';
    } else {
        uploadSection.classList.remove('hidden');
        manualEntrySection.classList.add('hidden');
        currentMode = 'upload';
    }
}

// Manual Entry Functions
function addManualItem() {
    const itemName = itemInput.value.trim();
    const quantity = quantityInput.value.trim();
    
    if (!itemName) {
        showMessage('Please enter an item name', 'error');
        return;
    }
    
    const item = {
        name: itemName,
        quantity: quantity || '1',
        id: Date.now()
    };
    
    groceryItems.push(item);
    renderItemsList();
    
    // Clear inputs
    itemInput.value = '';
    quantityInput.value = '';
    itemInput.focus();
    
    showMessage('Item added successfully!', 'success');
}

function renderItemsList() {
    itemsContainer.innerHTML = '';
    
    groceryItems.forEach(item => {
        const itemTag = document.createElement('div');
        itemTag.className = 'item-tag';
        itemTag.innerHTML = `
            <span>${item.name} (${item.quantity})</span>
            <button class="remove-btn" onclick="removeItem(${item.id})">×</button>
        `;
        itemsContainer.appendChild(itemTag);
    });
}

function removeItem(itemId) {
    groceryItems = groceryItems.filter(item => item.id !== itemId);
    renderItemsList();
}

// Receipt Processing (Backend API)
async function processReceiptImage(file) {
    showProcessing();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/process-receipt', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            groceryItems = result.items.map((item, index) => ({
                ...item,
                id: Date.now() + index
            }));
            showParsedItems();
        } else {
            showMessage('Error processing receipt: ' + result.error, 'error');
            resetToStart();
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        resetToStart();
    }
}

// UI State Management
function showProcessing() {
    uploadSection.classList.add('hidden');
    manualEntrySection.classList.add('hidden');
    processingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
}

function showParsedItems() {
    processingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    renderParsedItems();
    generateMealPlan();
}

function renderParsedItems() {
    const parsedItemsGrid = document.getElementById('parsedItemsGrid');
    parsedItemsGrid.innerHTML = '';
    
    groceryItems.forEach(item => {
        const itemCard = document.createElement('div');
        itemCard.className = 'item-card';
        itemCard.innerHTML = `
            <div class="item-name">${item.name}</div>
            <div class="item-quantity">${item.quantity}</div>
        `;
        parsedItemsGrid.appendChild(itemCard);
    });
}

// Meal Plan Generation (Backend API)
async function generateMealPlan() {
    if (groceryItems.length === 0) {
        showMessage('Please add some grocery items first', 'error');
        return;
    }
    
    showProcessing();
    
    try {
        const response = await fetch('/api/generate-meal-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: groceryItems.map(item => ({
                    name: item.name,
                    quantity: item.quantity
                }))
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            renderMealPlan(result.meal_plan);
            renderShoppingList(result.shopping_list);
            
            processingSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            
            // Store plan ID for potential saves
            window.currentPlanId = result.plan_id;
        } else {
            showMessage('Error generating meal plan: ' + result.error, 'error');
            resetToStart();
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        resetToStart();
    }
}

function renderMealPlan(mealPlan) {
    const mealPlanGrid = document.getElementById('mealPlanGrid');
    mealPlanGrid.innerHTML = '';
    
    Object.entries(mealPlan).forEach(([day, meals]) => {
        const dayCard = document.createElement('div');
        dayCard.className = 'day-card';
        
        dayCard.innerHTML = `
            <div class="day-title">${day}</div>
            <div class="meal-item">
                <div class="meal-name">Breakfast: ${meals.breakfast.name}</div>
                <div class="meal-ingredients">${meals.breakfast.ingredients.join(', ')}</div>
            </div>
            <div class="meal-item">
                <div class="meal-name">Lunch: ${meals.lunch.name}</div>
                <div class="meal-ingredients">${meals.lunch.ingredients.join(', ')}</div>
            </div>
            <div class="meal-item">
                <div class="meal-name">Dinner: ${meals.dinner.name}</div>
                <div class="meal-ingredients">${meals.dinner.ingredients.join(', ')}</div>
            </div>
        `;
        
        mealPlanGrid.appendChild(dayCard);
    });
}

function renderShoppingList(shoppingList) {
    const shoppingListContent = document.getElementById('shoppingListContent');
    shoppingListContent.innerHTML = '';
    
    if (shoppingList.length === 0) {
        shoppingListContent.innerHTML = '<p>You have all the essential items! Great job!</p>';
        return;
    }
    
    shoppingList.forEach(item => {
        const shoppingItem = document.createElement('div');
        shoppingItem.className = 'shopping-item';
        shoppingItem.innerHTML = `
            <input type="checkbox" class="shopping-checkbox" id="shop-${item.name.replace(/\s+/g, '-')}">
            <label for="shop-${item.name.replace(/\s+/g, '-')}">
                <strong>${item.name}</strong> - ${item.reason}
                ${item.priority ? `<span class="priority-${item.priority}">(${item.priority})</span>` : ''}
            </label>
        `;
        shoppingListContent.appendChild(shoppingItem);
    });
}

// Utility Functions
function showMessage(message, type) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#f56565' : '#48bb78'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

function resetToStart() {
    groceryItems = [];
    currentMode = 'upload';
    
    // Reset UI
    uploadSection.classList.remove('hidden');
    manualEntrySection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    
    // Reset form
    manualEntryCheckbox.checked = false;
    itemInput.value = '';
    quantityInput.value = '';
    fileInput.value = '';
    
    // Clear items list
    itemsContainer.innerHTML = '';
    
    showMessage('Ready to create a new meal plan!', 'success');
}

// Add slide animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('Receipt to Meal Planner initialized!');
    showMessage('Welcome! Upload a receipt or enter items manually to get started.', 'success');
});
