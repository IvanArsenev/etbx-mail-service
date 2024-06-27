import uvicorn, jwt, re, os
from fastapi import Depends, status, FastAPI, HTTPException, Query, File, UploadFile, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from PIL import Image
import requests
from sqlalchemy import create_engine
import sqlalchemy.orm as sqlorm
from sqlalchemy.orm import sessionmaker
from config import *
from classes import *
from datetime import datetime
from cryptography.fernet import Fernet
from bs4 import BeautifulSoup
import imaplib
import email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить доступ с любых доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
cipher_suite = Fernet(FORNET_KEY)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlorm.declarative_base()


def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

def fetch_email_attachment(email_user, app_password, mail_id, filename, folder="All Mail", imap_server="mail.pmc-python.ru", save_path="files"):
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    try:
        mail.login(email_user, app_password)
    except:
        return 'Error', ''
    mail.select(folder)
    status, messages = mail.search(None, 'ALL')
    mail_ids = messages[0].split()
    if mail_id.encode() not in mail_ids:
        mail.logout()
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    status, msg_data = mail.fetch(mail_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        part_filename = part.get_filename()
                        if part_filename:
                            decoded_filename, encoding = decode_header(part_filename)[0]
                            if isinstance(decoded_filename, bytes):
                                part_filename = decoded_filename.decode(encoding if encoding else "utf-8")
                            if part_filename == filename:
                                file_data = part.get_payload(decode=True)
                                os.makedirs(save_path, exist_ok=True)
                                file_path = os.path.join(save_path, f'{folder}_${mail_id}_${filename}')
                                with open(file_path, "wb") as f:
                                    f.write(file_data)
                                mail.logout()
                                return file_path, part.get_content_type()
    mail.logout()
    raise HTTPException(status_code=404, detail="Вложение не найдено")

def encrypt_password(password: str) -> str:
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

def get_user_by_email(email):
    return SessionLocal().query(User).filter(User.mail == email).first()

def check_available_token(token):
    try:
        db = SessionLocal()
        disabled_token = db.query(DisabledTokens).filter(DisabledTokens.token == token).first()
        return disabled_token is not None
    finally:
        db.close()

def login_and_fetch_emails(email_user, app_password, folder="All Mail", unseen='ALL', imap_server="mail.pmc-python.ru"):
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    try:
        mail.login(email_user, app_password)
    except:
        return 'Error'
    status, folders = mail.list()
    try:
        mail.select(folder)
        status, messages = mail.search(None, unseen)
    except:
        if folder == 'Sent':
            for index, folder in enumerate(folders):
                if b'\\Sent' in folder:
                    decoded_folder = folder.decode('utf-8')
                    match = re.search(r'"/" "([^"]+)"', decoded_folder)
                    mail.select(match.group(1))
                    status, messages = mail.search(None, unseen)
                    break
        else:
            return 'Error'
    mail_ids = messages[0].split()
    emails = []
    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                try:
                    subject, encoding = decode_header(msg["Subject"])[0]
                except:
                    subject, encoding = decode_header("None")[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")
                from_name, from_addr = email.utils.parseaddr(from_)
                decoded_from_name, encoding = decode_header(from_name)[0]
                if isinstance(decoded_from_name, bytes):
                    decoded_from_name = decoded_from_name.decode(encoding if encoding else "utf-8")
                from_ = f"{decoded_from_name} <{from_addr}>"
                to = msg.get("To")
                to_name, to_addr = email.utils.parseaddr(to)
                decoded_to_name, encoding = decode_header(to_name)[0]
                if isinstance(decoded_to_name, bytes):
                    decoded_to_name = decoded_to_name.decode(encoding if encoding else "utf-8")
                to = f"{decoded_to_name} <{to_addr}>"
                date_ = msg.get("Date")
                date_tuple = None
                if date_ is None:
                    received_header = msg.get("Received")
                    if received_header:
                        date_part = received_header.split(';')[-1].strip()
                        date_tuple = email.utils.parsedate_tz(date_part)
                else:
                    date_tuple = email.utils.parsedate_tz(date_)
                if date_tuple:
                    local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                    formatted_date = local_date.strftime("%H:%M %d.%m.%Y")
                else:
                    formatted_date = "Не удалось распознать дату"
                body = ""
                files = []
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                decoded_filename, encoding = decode_header(filename)[0]
                                if isinstance(decoded_filename, bytes):
                                    filename = decoded_filename.decode(encoding if encoding else "utf-8")
                                unique_filename = f"{folder}_${mail_id.decode()}_${filename}"
                                files.append(unique_filename)
                        else:
                            try:
                                part_body = part.get_payload(decode=True).decode()
                                if content_type == "text/plain":
                                    body += part_body
                                elif content_type == "text/html":
                                    soup = BeautifulSoup(part_body, "html.parser")
                                    body += soup.get_text()
                            except:
                                pass
                else:
                    body = msg.get_payload(decode=True).decode()
                    if msg.get_content_type() == "text/html":
                        soup = BeautifulSoup(body, "html.parser")
                        body = soup.get_text()
                email_data = {
                    "id": mail_id.decode(),
                    "subject": subject,
                    "body": body.strip(),
                    "sender": from_,
                    "recipient": to,
                    "received_time": formatted_date,
                    "files": files
                }
                emails.append(email_data)
    mail.logout()
    return emails

def send_email(email_user, email_password, to_address, subject, message, smtp_server = "mail.pmc-python.ru", smtp_port = 587):
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        return True
    except Exception as e:
        return False
    # finally:
    #     server.quit()

def parse_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%H:%M %d.%m.%Y")

def get_senders(combined_data, f_name):
    senders = set()
    for message in combined_data:
        sender = message.get(f_name)
        if sender:
            senders.add(sender)
    return list(senders)


@app.get("/users/me", tags=["Profile"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    user = {
        "id": current_user.id,
        "Имя": current_user.name,
        "Фамилия": current_user.surname,
        "Дата рождения": current_user.birthday,
        "Пол": current_user.gender,
        "Логин": current_user.mail,
        "Номер_телефона": current_user.phone_num if current_user.phone_num else None,
        "Аватар": current_user.avatar,
        "token": current_user.token
    }
    return user

@app.get("/users/{id}", tags=["Users"])
async def read_user_id(id: str):
    user_db = SessionLocal().query(User).filter(User.id == id).first()
    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с id {id} не найден!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = {
        "id": user_db.id,
        "Имя": user_db.name,
        "Фамилия": user_db.surname,
        "Дата рождения": user_db.birthday,
        "Пол": user_db.gender,
        "Логин": user_db.mail,
        "Номер_телефона": user_db.phone_num if user_db.phone_num else None,
        "Аватар": user_db.avatar
    }
    return user

@app.get("/users", tags=["Users"], response_model=PaginatedUsersResponse)
async def get_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    db = SessionLocal()
    total_users = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    formatted_users = []
    for user in users:
        formatted_users.append(UsersResponse(
            id=user.id,
            Имя=user.name,
            Фамилия=user.surname,
            Дата_рождения=user.birthday,
            Пол=user.gender,
            Почта=user.mail,
            Номер_телефона=user.phone_num if user.phone_num else None,
            Аватар=user.avatar
        ))
    db.close()
    return {
        "total_users": total_users,
        "users": formatted_users
    }

@app.post("/register", tags=["Auth"])
async def register_user(registration_request: RegistrationRequest):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.mail == f'{registration_request.mail}@pmc-python.ru').first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже зарегистрирован")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"https://pmc-python.ru/api/v1/user/{registration_request.mail}@pmc-python.ru", headers=headers)
    if response:
        db.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже зарегистрирован")
    encrypted_password = encrypt_password(registration_request.password)
    new_user = User(
        name=registration_request.name,
        surname=registration_request.surname,
        birthday=registration_request.birthday,
        gender=registration_request.gender,
        mail=f'{registration_request.mail}@pmc-python.ru',
        phone_num=registration_request.phone_num,
        password=encrypted_password,
        token=create_access_token(data={"sub": f'{registration_request.mail}@pmc-python.ru'})
    )
    external_api_data = {
        "email": f'{registration_request.mail}@pmc-python.ru',
        "raw_password": registration_request.password,
        "displayed_name": f"{registration_request.name} {registration_request.surname}"
    }
    response = requests.post("https://pmc-python.ru/api/v1/user", json=external_api_data, headers=headers)
    if response.status_code != 201 and response.status_code != 200:
        db.close()
        raise HTTPException(status_code=502, detail=f"Ошибка регистрации на внешнем сервере. Текст ошибки: {response.text}")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"Token": new_user.token}

@app.post("/login", tags=["Auth"])
async def login_for_access_token(form_data: LoginRequest):
    mail_ru_domens = ['mail.ru', 'internet.ru', 'bk.ru', 'inbox.ru', 'list.ru']
    if form_data.email.split('@')[1] == "pmc-python.ru":
        user = get_user_by_email(form_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный логин или пароль!",
                headers={"WWW-Authenticate": "Bearer"},
            )
        decrypted_password = decrypt_password(user.password)
        if form_data.password != decrypted_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not(check_available_token(user.token)):
            return {"Token": user.token}
        db = SessionLocal()
        disabled_token = db.query(DisabledTokens).filter(DisabledTokens.token == user.token).first()
        if disabled_token:
            db.delete(disabled_token)
            db.commit()
        db.close()
        return {"Token": user.token}
    elif form_data.email.split('@')[1] in mail_ru_domens:
        mail = imaplib.IMAP4_SSL('imap.mail.ru', 993)
        try:
            mail.login(f'{form_data.email}', f'{form_data.password}')
        except:
            return {"message": "Ошибка. Некорректные данные для входа!"}
        db = SessionLocal()
        encrypted_password = encrypt_password(form_data.password)
        user_name = 'Имя'
        user_surname = 'Фамилия'
        user_birthday = '01-01-2000'
        user_gender = 'None'
        new_user = User(
            name=user_name,
            surname=user_surname,
            birthday=user_birthday,
            gender=user_gender,
            mail=form_data.email,
            phone_num=None,
            password=encrypted_password,
            token=create_access_token(data={"sub": f'{form_data.email}'})
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        return {"Token": new_user.token}
    else:
        return {"message": "Ошибка. Некорректные данные для входа!"}

@app.get("/avatars/{image_name}", tags=["Users"])
async def get_image(image_name: str):
    return {"message": f"Requesting image: {image_name}"}

@app.put("/edit_avatar", tags=["Profile"])
async def edit_avatar(avatar: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    if not avatar.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Неверный формат файла!")
    MAX_SIZE = 10 * 1024 * 1024
    await avatar.seek(0)
    file_content = await avatar.read()
    if len(file_content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Размер файла слишком большой (не более 10 Мб)!")
    avatar.file.seek(0)
    try:
        with Image.open(avatar.file) as img:
            width, height = img.size
            if height > width and height > 512:
                new_height = 512
                new_width = int((new_height / height) * width)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            elif width > height and width > 512:
                new_width = 512
                new_height = int((new_width / width) * height)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            elif width == height and width > 512:
                new_width = 512
                new_height = 512
                img = img.resize((new_width, new_height), Image.LANCZOS)
            save_path = Path(f"./avatars/{current_user.id}.png")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path, format="PNG")
        db = SessionLocal()
        db_user = db.query(User).filter(User.id == current_user.id).first()
        db_user.avatar = f"avatars/{current_user.id}.png"
        db.commit()
        db.close()
        return {"message": "Аватар успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")

@app.delete("/remove_avatar", tags=["Profile"])
async def remove_avatar(current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    try:
        avatar_path = Path(f"./avatars/{current_user.id}.png")
        if avatar_path.exists():
            avatar_path.unlink()
            db = SessionLocal()
            db_user = db.query(User).filter(User.id == current_user.id).first()
            db_user.avatar = None
            db.commit()
            db.close()
            return {"message": "Аватар успешно удален"}
        else:
            raise HTTPException(status_code=404, detail="Аватар не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении аватара: {str(e)}")

@app.put("/edit", tags=["Profile"])
async def edit_me(updated_profile: EditProfile, current_user: dict = Depends(get_current_user)):
    if current_user.mail.split('@')[1] != "pmc-python.ru" and updated_profile.password is not None:
        return {"message": "Вы не можете измениить пароль от импортированного аккаунта!"}
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    encrypted_password = encrypt_password(updated_profile.password)
    fields_to_update = {}
    if updated_profile.name is not None: fields_to_update['name'] = updated_profile.name
    else: fields_to_update['name'] = current_user.name
    if updated_profile.surname is not None: fields_to_update['surname'] = updated_profile.surname
    else: fields_to_update['surname'] = current_user.surname
    if updated_profile.birthday is not None: fields_to_update['birthday'] = updated_profile.birthday
    if updated_profile.gender is not None: fields_to_update['gender'] = updated_profile.gender
    # if updated_profile.mail is not None: fields_to_update['mail'] = updated_profile.mail
    if updated_profile.phone_num is not None: fields_to_update['phone_num'] = updated_profile.phone_num
    if updated_profile.password is not None: fields_to_update['password'] = encrypted_password
    else: fields_to_update['password'] = encrypt_password(current_user.password)

    external_api_data = {
        "raw_password": fields_to_update['password'],
        "displayed_name": f"{fields_to_update['name']} {fields_to_update['surname']}"
    }
    response = requests.patch(f"https://pmc-python.ru/api/v1/user/{current_user.mail}", json=external_api_data, headers=headers)
    if response.status_code != 201 and response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Ошибка изменения данных на внешнем сервере. Текст ошибки: {response.text}")
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.id == current_user.id).first()
        for field, value in fields_to_update.items():
            setattr(db_user, field, value)
        db.commit()
        db.close()
        return {"message": "Профиль успешно обновлен"}
    except:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении профиля")

@app.post("/logout", tags=["Auth"])
async def logout(current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Вы не в системе!"}
    db = SessionLocal()
    disabled_token = DisabledTokens(token=current_user.token)
    db.add(disabled_token)
    db.commit()
    db.close()
    return {"message": "Вы успешно вышли из системы"}

@app.get("/messages/{folder}", tags=["Chat"])
async def get_messages(folder: str, current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        if folder == 'noread':
            emails = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox', 'UNSEEN', imap_server='imap.mail.ru')
        else:
            emails = login_and_fetch_emails(f'{current_user.mail}', decoded_password, folder, imap_server='imap.mail.ru')
    else:
        if folder == 'noread':
            emails = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox', 'UNSEEN')
        else:
            emails = login_and_fetch_emails(f'{current_user.mail}', decoded_password, folder)
    formatted_emails = [
        {
            "id": email["id"],
            "Тема": email["subject"],
            "Сообщение": email["body"],
            "Отправитель": email["sender"],
            "Получатель": email["recipient"],
            "Время получения": email["received_time"],
            "Файлы": email["files"]
        }
        for email in emails
    ]
    return {"messages": formatted_emails}

@app.post("/send", tags=["Chat"])
async def send_msg(message: Message, current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Вы не в системе!"}
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        check = send_email(f'{current_user.mail}', decoded_password, message.receiver, message.theme, message.body, smtp_server = 'imap.mail.ru')
    else:
        check = send_email(f'{current_user.mail}', decoded_password, message.receiver, message.theme, message.body)
    if check:
        return {"message": "Сообщение отправлено"}
    else:
        return {"message": "Ошибка. Некорректный токен!"}

@app.get("/get_my_chats", tags=["Chat"])
async def get_users_chats(current_user: dict = Depends(get_current_user)):
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent', imap_server = 'imap.mail.ru')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        senders_2 = get_senders(emails_out, 'recipient')

        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox', imap_server = 'imap.mail.ru')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        senders_1 = get_senders(emails_in, 'sender')
        
    else:
        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        senders_1 = get_senders(emails_in, 'sender')
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        senders_2 = get_senders(emails_out, 'recipient')
    combined_data = senders_1 + senders_2
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    unique_emails = set()
    for s in combined_data:
        emails = re.findall(email_pattern, s)
        unique_emails.update(emails)
    unique_emails_list = list(unique_emails)
    return {"chats": unique_emails_list}
    
@app.get("/get_themes_of_chat/{interlocutor}", tags=["Chat"])
async def get_themes_of_chats(interlocutor: str, current_user: dict = Depends(get_current_user)):
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox', imap_server = 'imap.mail.ru')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_in = [item for item in emails_in if interlocutor in item['sender']]
        senders_1 = get_senders(filtered_emails_in, 'subject')
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent', imap_server = 'imap.mail.ru')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_out = [item for item in emails_out if interlocutor in item['recipient']]
        senders_2 = get_senders(filtered_emails_out, 'subject')
    else:
        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_in = [item for item in emails_in if interlocutor in item['sender']]
        senders_1 = get_senders(filtered_emails_in, 'subject')
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_out = [item for item in emails_out if interlocutor in item['recipient']]
        senders_2 = get_senders(filtered_emails_out, 'subject')
    combined_data = senders_1 + senders_2
    list_of_themes = []
    for theme in combined_data:
        try:
            if theme[0:4] == 'Re: ':
                list_of_themes.append(theme[4:])
            else:
                list_of_themes.append(theme)
        except:
            list_of_themes.append(theme)
    unique_emails_list = list(set(list_of_themes))
    return {"themes": unique_emails_list}

@app.get("/get_messages_by_theme/{interlocutor}/{theme}", tags=["Chat"])
async def get_messages_in_themes_of_chats(interlocutor: str, theme: str, current_user: dict = Depends(get_current_user)):
    def clean_email_address(email):
        match = re.search(r'[\w\.-]+@[\w\.-]+', email)
        return match.group(0) if match else email
    def clean_subject(subject):
        return subject[4:] if subject.lower().startswith('re: ') else subject
    def parse_received_time(received_time):
        return datetime.strptime(received_time, "%H:%M %d.%m.%Y")
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox', imap_server = 'imap.mail.ru')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_in = [
            item for item in emails_in if interlocutor in item['sender'] and (theme == item['subject'] or theme == item['subject'][4:])
        ]
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent', imap_server = 'imap.mail.ru')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_out = [
            item for item in emails_out if interlocutor in item['recipient'] and (theme == item['subject'] or theme == item['subject'][4:])
        ]
    else:
        emails_in = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'inbox')
        if emails_in == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_in = [
            item for item in emails_in if interlocutor in item['sender'] and (theme == item['subject'] or theme == item['subject'][4:])
        ]
        emails_out = login_and_fetch_emails(f'{current_user.mail}', decoded_password, 'Sent')
        if emails_out == 'Error': return {"message": "Ошибка. Некорректный токен!"}
        filtered_emails_out = [
            item for item in emails_out if interlocutor in item['recipient'] and (theme == item['subject'] or theme == item['subject'][4:])
        ]
    combined_data = filtered_emails_in + filtered_emails_out
    unique_emails_list = []
    for email in combined_data:
        cleaned_email = {
            "id": email["id"],
            "subject": clean_subject(email["subject"]),
            "body": email["body"],
            "sender": clean_email_address(email["sender"]),
            "recipient": clean_email_address(email["recipient"]),
            "received_time": email["received_time"],
            "parsed_received_time": parse_received_time(email["received_time"]),
            "files": email["files"]
        }
        unique_emails_list.append(cleaned_email)
    unique_emails_list.sort(key=lambda x: x["parsed_received_time"])
    for email in unique_emails_list:
        del email["parsed_received_time"]
    return {"messages": unique_emails_list}

@app.get("/attachments/{folder}/{mail_id}/{file_name}", tags=["Chat"])
async def get_attachment(folder: str, mail_id: str, file_name: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    decoded_password = decrypt_password(current_user.password)
    if current_user.mail.split('@')[1] != "pmc-python.ru":
        file_path, content_type = fetch_email_attachment(current_user.mail, decoded_password, mail_id, file_name, folder, imap_server = 'imap.mail.ru')
    else:
        file_path, content_type = fetch_email_attachment(current_user.mail, decoded_password, mail_id, file_name, folder)
    if file_path == 'Error': return {"message": "Ошибка. Некорректный токен!"}
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден!")
    background_tasks.add_task(delete_file, file_path)
    return FileResponse(file_path, media_type=content_type, filename=file_name)


uvicorn.run(app, host=run_host, port=run_port)