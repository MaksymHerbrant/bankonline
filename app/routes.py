from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, flash, send_file
from app.models import User, Account, Transaction, Loan, Card, Deposit, News
from app import db
from app.utils import (
    validate_ukrainian_phone, 
    validate_identification_code, 
    format_phone_number, 
    validate_full_name,
    is_phone_unique,
    is_identification_code_unique,
    generate_card_number,
    generate_cvv,
    generate_expiry_date,
    format_card_number
)
import random
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
import csv
import io
import os
import pytz

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@main_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        print(f"Отримані дані реєстрації: {data}")
        
        # Валідація ПІБ
        if not validate_full_name(data['full_name']):
            print("Помилка валідації ПІБ")
            return jsonify({'error': 'Невірний формат ПІБ. Введіть у форматі: Прізвище Ім\'я По-батькові'}), 400
        
        # Валідація номера телефону
        if not validate_ukrainian_phone(data['phone']):
            print("Помилка валідації номера телефону")
            return jsonify({'error': 'Невірний формат номера телефону'}), 400
        
        # Форматуємо номер телефону
        phone = data['phone']
        if not phone.startswith('+380'):
            phone = '+380' + phone
        
        print(f"Перевіряємо унікальність номера: {phone}")
        
        # Перевірка унікальності номера телефону
        if not is_phone_unique(phone):
            print("Номер телефону вже існує")
            return jsonify({'error': 'Користувач з таким номером телефону вже існує'}), 400
        
        # Валідація ідентифікаційного коду
        if not validate_identification_code(data['identification_code']):
            print("Помилка валідації ідентифікаційного коду")
            return jsonify({'error': 'Невірний ідентифікаційний код'}), 400
        
        # Перевірка унікальності ідентифікаційного коду
        if not is_identification_code_unique(data['identification_code']):
            print("Ідентифікаційний код вже існує")
            return jsonify({'error': 'Користувач з таким ідентифікаційним кодом вже існує'}), 400
        
        pin = str(random.randint(1000, 9999))
        print(f"Зберігаємо користувача з номером: {phone}")
        
        user = User(
            pin=pin,
            full_name=data['full_name'],
            phone=phone,
            identification_code=data['identification_code']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        print(f"Користувач створений з ID: {user.id}")
        
        account = Account(user_id=user.id)
        db.session.add(account)
        db.session.commit()
        print(f"Рахунок створений з ID: {account.id}")
        
        # Створюємо карту
        card = Card(
            card_number=generate_card_number().replace(' ', ''),
            cvv=generate_cvv(),
            expiry_date=generate_expiry_date(),
            user_id=user.id,
            account_id=account.id
        )
        db.session.add(card)
        db.session.commit()
        print(f"Карта створена з номером: {card.card_number}")
        
        return jsonify({
            'success': True,
            'pin': pin,
            'card': {
                'number': format_card_number(card.card_number),
                'cvv': card.cvv,
                'expiry_date': card.expiry_date.strftime('%m/%Y')
            }
        }), 201
        
    except Exception as e:
        print(f"Помилка при реєстрації: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при реєстрації'}), 500

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        print("GET запит на сторінку входу")
        return render_template('login.html')
        
    try:
        data = request.json
        print(f"Отримані дані входу: {data}")
        
        if not data or 'phone' not in data or 'password' not in data:
            print("Відсутні обов'язкові поля")
            return jsonify({'error': 'Відсутні обов\'язкові поля'}), 400
        
        # Перевіряємо, чи номер вже містить код країни
        phone = data['phone']
        if not phone.startswith('+380'):
            phone = '+380' + phone
        
        print(f"Шукаємо користувача з номером: {phone}")
        
        user = User.query.filter_by(phone=phone).first()
        print(f"Результат пошуку користувача: {user}")
        
        if not user:
            print(f"Користувач не знайдений: {phone}")
            return jsonify({'error': 'Користувача не знайдено'}), 401
        
        if not user.check_password(data['password']):
            print(f"Невірний пароль для користувача: {phone}")
            return jsonify({'error': 'Невірний пароль'}), 401
        
        print(f"Спроба входу користувача: {user.id}")
        login_user(user)
        print(f"Користувач успішно увійшов: {user.id}")
        
        # Повертаємо URL для перенаправлення
        dashboard_url = url_for('main.dashboard', _external=True)
        print(f"URL для перенаправлення: {dashboard_url}")
        
        return jsonify({
            'success': True,
            'redirect': dashboard_url
        }), 200
        
    except Exception as e:
        print(f"Помилка при вході: {str(e)}")
        return jsonify({'error': 'Помилка при вході в систему'}), 500

def create_card_for_user(user_id, account_id):
    try:
        # Перевіряємо, чи вже існує карта
        existing_card = Card.query.filter_by(user_id=user_id).first()
        if existing_card:
            return existing_card
            
        # Створюємо нову карту
        card = Card(
            card_number=generate_card_number().replace(' ', ''),
            cvv=generate_cvv(),
            expiry_date=generate_expiry_date(),
            user_id=user_id,
            account_id=account_id
        )
        db.session.add(card)
        db.session.commit()
        print(f"Створено нову карту для користувача {user_id}")
        return card
    except Exception as e:
        print(f"Помилка при створенні картки: {str(e)}")
        db.session.rollback()
        return None

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        user = User.query.get(current_user.id)
        if not user:
            return redirect(url_for('main.index'))
            
        account = Account.query.filter_by(user_id=user.id).first()
        if not account:
            account = Account(user_id=user.id)
            db.session.add(account)
            db.session.commit()
            
        card = Card.query.filter_by(user_id=user.id).first()
        if not card:
            card = Card(
                card_number=''.join([str(random.randint(0, 9)) for _ in range(16)]),
                cvv=''.join([str(random.randint(0, 9)) for _ in range(3)]),
                expiry_date=datetime.now() + timedelta(days=365*4),
                user_id=user.id,
                account_id=account.id
            )
            db.session.add(card)
            db.session.commit()
            
        # Додаємо київський часовий пояс
        kyiv_tz = pytz.timezone('Europe/Kiev')
        
        # Отримуємо та сортуємо транзакції
        transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.timestamp.desc()).all()
        
        # Конвертуємо час для всіх транзакцій
        for transaction in transactions:
            if transaction.timestamp.tzinfo is None:
                transaction.timestamp = pytz.UTC.localize(transaction.timestamp)
            
        return render_template('dashboard.html', user=user, account=account, card=card, transactions=transactions, kyiv_tz=kyiv_tz)
    except Exception as e:
        print(f"Помилка при доступі до dashboard: {str(e)}")
        return redirect(url_for('main.index'))

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/deposit', methods=['GET'])
@login_required
def deposit_page():
    try:
        user = User.query.get(current_user.id)
        if not user:
            return redirect(url_for('main.index'))
            
        deposits = Deposit.query.filter_by(user_id=user.id).all()
        return render_template('deposit.html', user=user, deposits=deposits)
    except Exception as e:
        print(f"Помилка при доступі до сторінки депозиту: {str(e)}")
        return redirect(url_for('main.index'))

@main_bp.route('/deposit', methods=['POST'])
@login_required
def create_deposit():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        amount = float(data['amount'])
        term = int(data['term'])
        
        if amount <= 0:
            return jsonify({'error': 'Сума депозиту повинна бути більше 0'}), 400
            
        # Перевіряємо баланс
        account = Account.query.filter_by(user_id=user.id).first()
        if not account or account.balance < amount:
            return jsonify({'error': 'Недостатньо коштів на рахунку'}), 400
            
        # Створюємо депозит
        deposit = Deposit(
            amount=amount,
            term=term,
            interest_rate=0.15,  # 15% річних
            user_id=user.id
        )
        
        # Зменшуємо баланс рахунку
        account.balance -= amount
        
        # Створюємо транзакцію
        current_time = pytz.UTC.localize(datetime.now())
        transaction = Transaction(
            amount=-amount,
            type='deposit',
            account_id=account.id,
            timestamp=current_time
        )
        
        db.session.add(deposit)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Помилка при створенні депозиту: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при створенні депозиту'}), 500

@main_bp.route('/credit')
@login_required
def credit():
    try:
        user = User.query.get(current_user.id)
        if not user:
            return redirect(url_for('main.index'))
            
        loans = Loan.query.filter_by(user_id=user.id).all()
        return render_template('credit.html', user=user, loans=loans)
    except Exception as e:
        print(f"Помилка при доступі до сторінки кредиту: {str(e)}")
        return redirect(url_for('main.index'))

@main_bp.route('/settings')
@login_required
def settings():
    try:
        user = User.query.get(current_user.id)
        if not user:
            return redirect(url_for('main.index'))
            
        return render_template('settings.html', user=user)
    except Exception as e:
        print(f"Помилка при доступі до сторінки налаштувань: {str(e)}")
        return redirect(url_for('main.index'))

@main_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Невірний поточний пароль'}), 401
            
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Помилка при зміні пароля: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при зміні пароля'}), 500

@main_bp.route('/change-phone', methods=['POST'])
@login_required
def change_phone():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        new_phone = data['new_phone']
        if not new_phone.startswith('+380'):
            new_phone = '+380' + new_phone
            
        # Перевіряємо, чи не використовується цей номер іншим користувачем
        existing_user = User.query.filter_by(phone=new_phone).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Цей номер телефону вже використовується'}), 400
            
        user.phone = new_phone
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Помилка при зміні номера телефону: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при зміні номера телефону'}), 500

@main_bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        amount = float(data['amount'])
        recipient_phone = data['recipient_phone']
        
        if not recipient_phone.startswith('+380'):
            recipient_phone = '+380' + recipient_phone
            
        # Знаходимо отримувача
        recipient = User.query.filter_by(phone=recipient_phone).first()
        if not recipient:
            return jsonify({'error': 'Отримувача не знайдено'}), 404
            
        # Перевіряємо, чи не відправляє користувач самому собі
        if recipient.id == user.id:
            return jsonify({'error': 'Не можна відправити гроші самому собі'}), 400
            
        # Перевіряємо баланс відправника
        sender_account = Account.query.filter_by(user_id=user.id).first()
        if not sender_account or sender_account.balance < amount:
            return jsonify({'error': 'Недостатньо коштів на рахунку'}), 400
            
        # Знаходимо або створюємо рахунок отримувача
        recipient_account = Account.query.filter_by(user_id=recipient.id).first()
        if not recipient_account:
            recipient_account = Account(user_id=recipient.id)
            db.session.add(recipient_account)
            
        # Виконуємо переказ
        sender_account.balance -= amount
        recipient_account.balance += amount
        
        # Створюємо транзакції з часом в UTC
        current_time = pytz.UTC.localize(datetime.now())
        
        sender_transaction = Transaction(
            amount=-amount,
            type='transfer_out',
            account_id=sender_account.id,
            recipient_id=recipient.id,
            timestamp=current_time
        )
        
        recipient_transaction = Transaction(
            amount=amount,
            type='transfer_in',
            account_id=recipient_account.id,
            recipient_id=user.id,
            timestamp=current_time
        )
        
        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_balance': sender_account.balance
        }), 200
    except Exception as e:
        print(f"Помилка при переказі коштів: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при переказі коштів'}), 500

@main_bp.route('/credit', methods=['POST'])
@login_required
def create_credit():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        amount = float(data['amount'])
        term_months = int(data['term_months'])
        purpose = data['purpose']
        
        if amount <= 0:
            return jsonify({'error': 'Сума кредиту повинна бути більше 0'}), 400
            
        # Визначаємо відсоткову ставку в залежності від мети
        interest_rate = 0.02  # 2% на місяць за замовчуванням
        if purpose == 'car':
            interest_rate = 0.015  # 1.5% на місяць
        elif purpose == 'mortgage':
            interest_rate = 0.01  # 1% на місяць
            
        # Створюємо кредит
        loan = Loan(
            amount=amount,
            interest_rate=interest_rate,
            term_months=term_months,
            remaining_balance=amount,
            user_id=user.id
        )
        
        # Знаходимо або створюємо рахунок
        account = Account.query.filter_by(user_id=user.id).first()
        if not account:
            account = Account(user_id=user.id)
            db.session.add(account)
            
        # Збільшуємо баланс рахунку
        account.balance += amount
        
        # Створюємо транзакцію
        current_time = pytz.UTC.localize(datetime.now())
        transaction = Transaction(
            amount=amount,
            type='credit',
            account_id=account.id,
            timestamp=current_time
        )
        
        db.session.add(loan)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Помилка при створенні кредиту: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при створенні кредиту'}), 500

@main_bp.route('/transfer-by-card', methods=['POST'])
@login_required
def transfer_by_card():
    try:
        data = request.json
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        amount = float(data['amount'])
        recipient_card = data['recipient_card']
        
        # Знаходимо отримувача за номером карти
        recipient_card_obj = Card.query.filter_by(card_number=recipient_card).first()
        if not recipient_card_obj:
            return jsonify({'error': 'Картку отримувача не знайдено'}), 404
            
        recipient = User.query.get(recipient_card_obj.user_id)
        if not recipient:
            return jsonify({'error': 'Отримувача не знайдено'}), 404
            
        # Перевіряємо, чи не відправляє користувач самому собі
        if recipient.id == user.id:
            return jsonify({'error': 'Не можна відправити гроші самому собі'}), 400
            
        # Перевіряємо баланс відправника
        sender_account = Account.query.filter_by(user_id=user.id).first()
        if not sender_account or sender_account.balance < amount:
            return jsonify({'error': 'Недостатньо коштів на рахунку'}), 400
            
        # Знаходимо або створюємо рахунок отримувача
        recipient_account = Account.query.filter_by(user_id=recipient.id).first()
        if not recipient_account:
            recipient_account = Account(user_id=recipient.id)
            db.session.add(recipient_account)
            
        # Виконуємо переказ
        sender_account.balance -= amount
        recipient_account.balance += amount
        
        # Створюємо транзакції з часом в UTC
        current_time = pytz.UTC.localize(datetime.now())
        
        sender_transaction = Transaction(
            amount=-amount,
            type='transfer_out',
            account_id=sender_account.id,
            recipient_id=recipient.id,
            timestamp=current_time
        )
        
        recipient_transaction = Transaction(
            amount=amount,
            type='transfer_in',
            account_id=recipient_account.id,
            recipient_id=user.id,
            timestamp=current_time
        )
        
        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_balance': sender_account.balance
        }), 200
    except Exception as e:
        print(f"Помилка при переказі коштів: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Помилка при переказі коштів'}), 500

@main_bp.route('/export-transactions')
@login_required
def export_transactions():
    try:
        user = User.query.get(current_user.id)
        if not user:
            return jsonify({'error': 'Користувача не знайдено'}), 404
            
        account = Account.query.filter_by(user_id=user.id).first()
        if not account:
            return jsonify({'error': 'Рахунок не знайдено'}), 404
            
        # Створюємо CSV файл в пам'яті
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Записуємо заголовки
        writer.writerow(['Дата', 'Тип операції', 'Сума', 'Отримувач/Відправник'])
        
        # Отримуємо всі транзакції
        transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.timestamp.desc()).all()
        
        # Конвертуємо час в київський часовий пояс
        kyiv_tz = pytz.timezone('Europe/Kiev')
        
        # Записуємо транзакції
        for transaction in transactions:
            transaction_type = ''
            if transaction.type == 'transfer_out':
                transaction_type = f'Переказ: {transaction.recipient.full_name}'
            elif transaction.type == 'transfer_in':
                transaction_type = f'Отримано від: {transaction.recipient.full_name}'
            else:
                transaction_type = transaction.type
                
            # Конвертуємо час в київський часовий пояс
            kyiv_time = transaction.timestamp.astimezone(kyiv_tz)
                
            writer.writerow([
                kyiv_time.strftime('%d.%m.%Y %H:%M'),
                transaction_type,
                f"{transaction.amount:.2f} грн",
                transaction.recipient.full_name if transaction.recipient else '-'
            ])
            
        # Створюємо відповідь
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'transactions_{datetime.now(kyiv_tz).strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        print(f"Помилка при експорті транзакцій: {str(e)}")
        return jsonify({'error': 'Помилка при експорті транзакцій'}), 500

@main_bp.route('/news')
def news_page():
    news_list = News.query.filter_by(is_active=True).order_by(News.date.desc()).all()
    return render_template('news.html', news_list=news_list)