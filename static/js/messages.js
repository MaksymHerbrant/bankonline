// Зберігаємо оригінальну функцію alert
const originalAlert = window.alert;

// Функція для отримання випадкового повідомлення від Чіпа та Дейла
function getChipDaleMessage(type) {
    const messages = {
        error: [
            "Чіп: Ой-ой! Щось пішло не так!",
            "Дейл: Можливо, варто спробувати ще раз?",
            "Чіп: Схоже, у нас виникла маленька проблемка!",
            "Дейл: Не хвилюйся, ми все виправимо!"
        ],
        success: [
            "Чіп: Ура! Все пройшло успішно!",
            "Дейл: Ми молодці!",
            "Чіп: Операція виконана на відмінно!",
            "Дейл: Все працює як годинник!"
        ],
        warning: [
            "Чіп: Гей, будь обережний!",
            "Дейл: Можливо, варто перевірити ще раз?",
            "Чіп: Здається, щось не так...",
            "Дейл: Давай переконаємося, що все правильно!"
        ]
    };
    
    const typeMessages = messages[type] || messages.error;
    return typeMessages[Math.floor(Math.random() * typeMessages.length)];
}

// Функція для показу повідомлення
function showMessage(message, type = 'error') {
    const chipDaleMessage = getChipDaleMessage(type);
    originalAlert(`${message}\n\n${chipDaleMessage}`);
}

// Перевизначаємо стандартну функцію alert
window.alert = function(message) {
    showMessage(message, 'info');
}; 