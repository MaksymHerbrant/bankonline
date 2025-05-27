document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    if (!form) {
        console.error('Форма реєстрації не знайдена');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fullName = document.getElementById('fullName')?.value;
        const phone = document.getElementById('phone')?.value;
        const identificationCode = document.getElementById('identificationCode')?.value;
        const password = document.getElementById('password')?.value;
        
        if (!fullName || !phone || !identificationCode || !password) {
            alert('Будь ласка, заповніть всі поля');
            return;
        }
        
        // Валідація ПІБ
        const nameRegex = /^[А-ЯІЇЄҐ][а-яіїєґ'-]+ [А-ЯІЇЄҐ][а-яіїєґ'-]+ [А-ЯІЇЄҐ][а-яіїєґ'-]+$/;
        if (!nameRegex.test(fullName)) {
            alert('Невірний формат ПІБ. Введіть у форматі: Прізвище Ім\'я По-батькові');
            return;
        }
        
        // Форматуємо номер телефону
        const formattedPhone = phone.startsWith('+380') ? phone : '+380' + phone;
        
        const data = {
            full_name: fullName,
            phone: formattedPhone,
            identification_code: identificationCode,
            password: password
        };
        
        console.log('Відправляємо дані реєстрації:', data);
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            console.log('Відповідь сервера:', result);
            
            if (response.ok) {
                alert(`Реєстрація успішна!\nВаш PIN: ${result.pin}\nНомер картки: ${result.card.number}\nCVV: ${result.card.cvv}\nТермін дії: ${result.card.expiry_date}`);
                window.location.href = '/';
            } else {
                alert(result.error || 'Помилка при реєстрації');
            }
        } catch (error) {
            console.error('Помилка:', error);
            alert('Помилка при спробі реєстрації');
        }
    });
}); 