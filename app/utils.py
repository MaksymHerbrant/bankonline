import random
import string
from datetime import datetime, timedelta
import re

def generate_account_number():
    return ''.join(random.choices(string.digits, k=16))

def generate_pin():
    return ''.join(random.choices(string.digits, k=4))

def generate_card_number():
    """Генерація номера карти у форматі XXXX XXXX XXXX XXXX"""
    number = ''.join(random.choices(string.digits, k=16))
    return ' '.join([number[i:i+4] for i in range(0, 16, 4)])

def generate_cvv():
    """Генерація CVV коду"""
    return ''.join(random.choices(string.digits, k=3))

def generate_expiry_date():
    """Генерація дати закінчення терміну дії карти (5 років від поточної дати)"""
    return datetime.now() + timedelta(days=365*5)

def format_card_number(card_number):
    """Форматування номера карти для відображення"""
    return ' '.join([card_number[i:i+4] for i in range(0, 16, 4)])

def mask_card_number(card_number):
    """Маскування номера карти для безпеки"""
    return f"**** **** **** {card_number[-4:]}"

def calculate_loan_payments(amount, interest_rate, term_months):
    monthly_rate = interest_rate / 100 / 12
    total_payment = amount * (1 + monthly_rate * term_months)
    monthly_payment = total_payment / term_months
    return {
        'total_payment': round(total_payment, 2),
        'monthly_payment': round(monthly_payment, 2),
        'end_date': datetime.now() + timedelta(days=30*term_months)
    }

def validate_full_name(full_name):
    """
    Валідація повного імені (ПІБ)
    Формат: Прізвище Ім'я По-батькові
    """
    # Видаляємо зайві пробіли
    full_name = ' '.join(full_name.split())
    
    # Перевіряємо, чи є три слова (прізвище, ім'я, по-батькові)
    parts = full_name.split()
    if len(parts) != 3:
        return False
    
    # Перевіряємо, чи кожна частина починається з великої літери
    for part in parts:
        if not part[0].isupper():
            return False
        # Перевіряємо, чи містить тільки літери, дефіс та апостроф
        if not all(c.isalpha() or c in ['-', "'", 'ʼ'] for c in part):
            return False
    
    return True

def validate_ukrainian_phone(phone):
    """
    Валідація українського номера телефону
    Формати: +380XXXXXXXXX або 0XXXXXXXXX
    """
    # Видаляємо всі символи крім цифр
    phone = re.sub(r'\D', '', phone)
    
    # Перевіряємо довжину (10 цифр для номера без коду країни)
    if len(phone) == 10 and phone.startswith('0'):
        return True
    # Перевіряємо довжину (12 цифр для номера з кодом країни)
    elif len(phone) == 12 and phone.startswith('380'):
        return True
    return False

def validate_identification_code(code):
    """
    Валідація ідентифікаційного коду
    """
    try:
        # Перевіряємо, чи код складається з 10 цифр
        if not code.isdigit() or len(code) != 10:
            print(f"Невірний формат ідентифікаційного коду: {code}")
            return False
            
        # Конвертуємо код в список цифр
        digits = [int(d) for d in code]
        
        # Перевіряємо контрольну суму
        checksum = (
            -1 * digits[0] + 5 * digits[1] + 7 * digits[2] + 9 * digits[3] +
            4 * digits[4] + 6 * digits[5] + 10 * digits[6] + 5 * digits[7] +
            7 * digits[8]
        ) % 11 % 10
        
        if checksum != digits[9]:
            print(f"Невірна контрольна сума для коду: {code}")
            return False
            
        print(f"Ідентифікаційний код {code} валідний")
        return True
    except Exception as e:
        print(f"Помилка при валідації ідентифікаційного коду: {str(e)}")
        return False

def format_phone_number(phone):
    """
    Форматування номера телефону у формат +380XXXXXXXXX
    """
    # Видаляємо всі символи крім цифр
    phone = re.sub(r'\D', '', phone)
    
    # Якщо номер починається з 0, замінюємо на 380
    if phone.startswith('0'):
        phone = '380' + phone[1:]
    # Якщо номер починається з 380, залишаємо як є
    elif phone.startswith('380'):
        phone = phone
    
    # Додаємо + на початок
    return '+' + phone

def is_phone_unique(phone):
    """
    Перевірка чи номер телефону унікальний
    """
    from app.models import User
    formatted_phone = format_phone_number(phone)
    return User.query.filter_by(phone=formatted_phone).first() is None

def is_identification_code_unique(code):
    """
    Перевірка унікальності ідентифікаційного коду
    """
    from app.models import User
    try:
        existing_user = User.query.filter_by(identification_code=code).first()
        if existing_user:
            print(f"Ідентифікаційний код {code} вже використовується")
            return False
        print(f"Ідентифікаційний код {code} унікальний")
        return True
    except Exception as e:
        print(f"Помилка при перевірці унікальності ідентифікаційного коду: {str(e)}")
        return False