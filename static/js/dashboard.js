let currentTicker = '';
let priceChart = null;
let predictionChart = null;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    
    const user = JSON.parse(localStorage.getItem('user'));
    document.getElementById('username').textContent = user.username;
    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Get auth headers
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    };
}

// Search stock
async function searchStock() {
    const ticker = document.getElementById('tickerInput').value.toUpperCase();
    if (!ticker) return;
    
    currentTicker = ticker;
    
    try {
        // Get current price
        const response = await fetch(`/api/stock/current/${ticker}`, {
            headers: getHeaders()
        });
        
        if (!response.ok) {
            alert('Stock not found!');
            return;
        }
        
        const data = await response.json();
        displayStockInfo(data);
        
        // Get history
        await loadHistory(ticker);
        
    } catch (error) {
        alert('Error fetching stock data');
        console.error(error);
    }
}

// Display stock information
function displayStockInfo(data) {
    document.getElementById('stockInfo').style.display = 'block';
    document.getElementById('stockName').textContent = data.info.name;
    document.getElementById('currentPrice').textContent = `$${data.price_data.price.toFixed(2)}`;
    document.getElementById('openPrice').textContent = `$${data.price_data.open.toFixed(2)}`;
    document.getElementById('highPrice').textContent = `$${data.price_data.high.toFixed(2)}`;
    document.getElementById('lowPrice').textContent = `$${data.price_data.low.toFixed(2)}`;
}

// Load price history
async function loadHistory(ticker) {
    try {
        const response = await fetch(`/api/stock/history/${ticker}?period=6mo`, {
            headers: getHeaders()
        });
        
        const data = await response.json();
        displayChart(data.history);
        
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Display price chart
function displayChart(history) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.dates,
            datasets: [{
                label: 'Close Price',
                data: history.close,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Historical Stock Price'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Get AI prediction
async function getPrediction() {
    if (!currentTicker) {
        alert('Please search for a stock first');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Predicting... (This may take a minute)';
    
    try {
        const response = await fetch(`/api/stock/predict/${currentTicker}`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ days: 7 })
        });
        
        const data = await response.json();
        displayPrediction(data);
        
        document.getElementById('predictionResult').style.display = 'block';
        
    } catch (error) {
        alert('Error generating prediction');
        console.error(error);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Predict Next 7 Days';
    }
}

// Display prediction chart
function displayPrediction(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    if (predictionChart) {
        predictionChart.destroy();
    }
    
    const dates = Array.from({length: 7}, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() + i + 1);
        return date.toLocaleDateString();
    });
    
    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Predicted Price',
                data: data.predictions,
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'AI Predicted Stock Prices (Next 7 Days)'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Initialize on page load
checkAuth();
