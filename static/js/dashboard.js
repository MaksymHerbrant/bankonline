// Функція для показу/приховування CVV
function toggleCVV() {
    const cvvElement = document.getElementById('cvv');
    const cvvText = document.querySelector('.cvv');
    
    if (cvvElement.classList.contains('d-none')) {
        cvvElement.classList.remove('d-none');
        cvvText.textContent = `CVV: ${cvvElement.textContent}`;
    } else {
        cvvElement.classList.add('d-none');
        cvvText.textContent = 'CVV: ***';
    }
}

// Функція для показу форми переказу
function showTransferForm() {
    const transferForm = document.getElementById('transfer-form');
    transferForm.style.display = 'block';
}

// Функція для приховування форми переказу
function hideTransferForm() {
    const transferForm = document.getElementById('transfer-form');
    transferForm.style.display = 'none';
}

// Обробник форми переказу
document.getElementById('transfer-form-inner').addEventListener('submit', function(e) {
    e.preventDefault();
    // Тут буде логіка переказу коштів
    alert('Переказ успішно виконано!');
    hideTransferForm();
});

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', function() {
    // Тут можна додати додаткову ініціалізацію
    console.log('Dashboard завантажено');
});

document.getElementById('transferForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        amount: parseFloat(document.getElementById('amount').value),
        accountId: 1 // Тимчасово хардкодимо ID акаунту
    };
    
    try {
        const response = await fetch('/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('balance').textContent = data.newBalance;
            alert('Переказ успішно виконано');
        } else {
            alert('Помилка переказу: ' + data.error);
        }
    } catch (error) {
        alert('Помилка при відправці форми');
    }
}); 