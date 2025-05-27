document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    if (!form) {
        console.error('Форма входу не знайдена');
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const phone = document.getElementById('phone')?.value;
        const password = document.getElementById('password')?.value;
        
        if (!phone || !password) {
            alert('Будь ласка, заповніть всі поля');
            return;
        }
        
        // Форматуємо номер телефону
        const formattedPhone = phone.startsWith('+380') ? phone : '+380' + phone;
        console.log('Відправляємо дані входу:', { phone: formattedPhone });
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    phone: formattedPhone,
                    password: password
                })
            });
            
            const data = await response.json();
            console.log('Відповідь сервера:', data);
            
            if (response.ok) {
                console.log('Успішний вхід, перенаправляємо на:', data.redirect);
                // Використовуємо window.location.href замість window.location.replace
                window.location.href = data.redirect;
            } else {
                alert(data.error || 'Помилка входу');
            }
        } catch (error) {
            console.error('Помилка:', error);
            alert('Помилка при спробі входу');
        }
    });
}); 