let currentUser = null;

async function login() {
    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            phone: document.querySelector('#login-phone').value,
            password: document.querySelector('#login-password').value
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        currentUser = data;
        showMainUI();
        updateBalance(data.balance);
        updateTransactions(data.transactions);
    } else {
        alert('Помилка входу');
    }
}

async function register() {
    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            fullName: document.querySelector('#register-name').value,
            phone: document.querySelector('#register-phone').value,
            password: document.querySelector('#register-password').value
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        alert(`Реєстрація успішна! Ваш PIN: ${data.pin}`);
        toggleForms();
    } else {
        alert('Помилка реєстрації');
    }
}

function showMainUI() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('main-nav').style.display = 'block';
    document.getElementById('home-page').style.display = 'block';
}

function updateBalance(amount) {
    document.getElementById('balance').textContent = 
        `${amount.toFixed(2)} грн`;
}

function updateTransactions(transactions) {
    const container = document.getElementById('transaction-history');
    container.innerHTML = transactions.map(t => `
        <div class="transaction-item">
            <div>${t.date}</div>
            <div>${t.type}</div>
            <div>${t.amount} грн</div>
        </div>
    `).join('');
}

// Функція для переключення між формами входу та реєстрації
function toggleForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (loginForm.classList.contains('d-none')) {
        loginForm.classList.remove('d-none');
        registerForm.classList.add('d-none');
    } else {
        loginForm.classList.add('d-none');
        registerForm.classList.remove('d-none');
    }
}

// Обробка форми входу
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = e.target.querySelector('input[type="text"]').value;
    const password = e.target.querySelector('input[type="password"]').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, password })
        });
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            alert('Помилка входу: ' + data.error);
        }
    } catch (error) {
        alert('Помилка при відправці форми');
    }
});

// Обробка форми реєстрації
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        fullName: e.target.querySelector('input[placeholder="ПІБ"]').value,
        phone: e.target.querySelector('input[placeholder="Номер телефону"]').value,
        password: e.target.querySelector('input[type="password"]').value
    };
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('pin-code').textContent = data.pin;
            alert(`Ваш PIN-код: ${data.pin}`);
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            alert('Помилка реєстрації: ' + data.error);
        }
    } catch (error) {
        alert('Помилка при відправці форми');
    }
});