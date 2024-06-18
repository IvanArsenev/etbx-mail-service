import uvicorn, jwt
from fastapi import Depends, status, FastAPI, HTTPException, Query, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
from PIL import Image
import requests
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
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

app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
cipher_suite = Fernet(FORNET_KEY)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



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

def login_and_fetch_emails(email_user, app_password, folder="All Mail", unseen = 'ALL', imap_server="mail.pmc-python.ru"):
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    mail.login(email_user, app_password)
    status, folders = mail.list()
    mail.select(folder)
    status, messages = mail.search(None, unseen)
    mail_ids = messages[0].split()
    emails = []
    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
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
                date_tuple = email.utils.parsedate_tz(date_)
                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                formatted_date = local_date.strftime("%H:%M %d.%m.%Y")
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" not in content_disposition:
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
                    "received_time": formatted_date
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
    finally:
        server.quit()



@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    date_obj = datetime.strptime(current_user.birthday, "%d-%m-%Y")
    formatted_date_str = date_obj.strftime("%d.%m.%Y")
    user = {
        "id": current_user.id,
        "Имя": current_user.name,
        "Фамилия": current_user.surname,
        "Дата рождения": formatted_date_str,
        "Пол": current_user.gender,
        "Логин": current_user.mail,
        "Номер_телефона": current_user.phone_num if current_user.phone_num else "Отсутствует",
        "Аватар": current_user.avatar,
        "token": current_user.token
    }
    return user

@app.get("/users/{id}")
async def read_user_id(id: str):
    user_db = SessionLocal().query(User).filter(User.id == id).first()
    date_obj = datetime.strptime(user_db.birthday, "%d-%m-%Y")
    formatted_date_str = date_obj.strftime("%d.%m.%Y")
    user = {
        "id": user_db.id,
        "Имя": user_db.name,
        "Фамилия": user_db.surname,
        "Дата рождения": formatted_date_str,
        "Пол": user_db.gender,
        "Логин": user_db.mail,
        "Номер_телефона": user_db.phone_num if user_db.phone_num else "Отсутствует",
        "Аватар": user_db.avatar
    }
    return user

@app.get("/users", response_model=PaginatedUsersResponse)
async def get_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    db = SessionLocal()
    total_users = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    formatted_users = []
    for user in users:
        date_obj = datetime.strptime(user.birthday, "%d-%m-%Y")
        formatted_date_str = date_obj.strftime("%d.%m.%Y")
        formatted_users.append(UsersResponse(
            id=user.id,
            Имя=user.name,
            Фамилия=user.surname,
            Дата_рождения=formatted_date_str,
            Пол=user.gender,
            Логин=user.mail,
            Номер_телефона=user.phone_num if user.phone_num else "Отсутствует",
            Аватар=user.avatar
        ))
    db.close()
    return {
        "total_users": total_users,
        "users": formatted_users
    }

@app.post("/register")
async def register_user(registration_request: RegistrationRequest):
    db = SessionLocal()
    
    encrypted_password = encrypt_password(registration_request.password)

    new_user = User(
        name=registration_request.name,
        surname=registration_request.surname,
        birthday=registration_request.birthday,
        gender=registration_request.gender,
        mail=f'{registration_request.mail}'+'@pmc-python.ru',
        phone_num=registration_request.phone_num,
        password=encrypted_password,
        token=create_access_token(data={"sub": registration_request.mail})
    )
    
    external_api_data = {
        "email": str(registration_request.mail)+'@pmc-python.ru',
        "raw_password": registration_request.password,
        "displayed_name": f"{registration_request.name} {registration_request.surname}"
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://pmc-python.ru/api/v1/user", json=external_api_data, headers=headers)

    if response.status_code != 201 and response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Registration failed on external server.")
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    user = get_user_by_email(form_data.email)
    if not(check_available_token(user.token)):
        return {"message": "Вы уже в системе"}
    
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
    db = SessionLocal()
    disabled_token = db.query(DisabledTokens).filter(DisabledTokens.token == user.token).first()
    if disabled_token:
        db.delete(disabled_token)
        db.commit()
    db.close()
    return {"Token": user.token}

@app.get("/avatars/{image_name}")
async def get_image(image_name: str):
    return {"message": f"Requesting image: {image_name}"}

@app.put("/edit_avatar")
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

@app.delete("/remove_avatar")
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

@app.put("/edit")
async def edit_me(updated_profile: EditProfile, current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    encrypted_password = encrypt_password(updated_profile.password)
    fields_to_update = {}
    if updated_profile.name is not None: fields_to_update['name'] = updated_profile.name
    if updated_profile.surname is not None: fields_to_update['surname'] = updated_profile.surname
    if updated_profile.birthday is not None: fields_to_update['birthday'] = updated_profile.birthday
    if updated_profile.gender is not None: fields_to_update['gender'] = updated_profile.gender
    if updated_profile.mail is not None: fields_to_update['mail'] = updated_profile.mail
    if updated_profile.phone_num is not None: fields_to_update['phone_num'] = updated_profile.phone_num
    if updated_profile.password is not None: fields_to_update['password'] = encrypted_password
    try:
        db = SessionLocal()
        db_user = db.query(User).filter(User.id == current_user.id).first()
        for field, value in fields_to_update.items():
            setattr(db_user, field, value)
        db.commit()
        db.close()
        return {"message": "Профиль успешно обновлен"}
    except:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении профиля")

@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Вы не в системе!"}
    db = SessionLocal()
    disabled_token = DisabledTokens(token=current_user.token)
    db.add(disabled_token)
    db.commit()
    db.close()
    return {"message": "Вы успешно вышли из системы"}

@app.get("/messages/{folder}")
async def get_messages(folder: str, current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Войдите в систему!"}
    decoded_password = decrypt_password(current_user.password)
    if folder == 'noread':
        emails = login_and_fetch_emails(f'{current_user.mail}@pmc-python.ru', decoded_password, 'inbox', 'UNSEEN')
    else:
        emails = login_and_fetch_emails(f'{current_user.mail}@pmc-python.ru', decoded_password, folder)
    formatted_emails = [
        {
            "id": email["id"],
            "Тема": email["subject"],
            "Сообщение": email["body"],
            "Отправитель": email["sender"],
            "Получатель": email["recipient"],
            "Время получения": email["received_time"]
        }
        for email in emails
    ]
    return {"messages": formatted_emails}

@app.post("/send")
async def send_msg(message: Message, current_user: dict = Depends(get_current_user)):
    if check_available_token(current_user.token):
        return {"message": "Вы не в системе!"}
    decoded_password = decrypt_password(current_user.password)
    check = send_email(f'{current_user.mail}@pmc-python.ru', decoded_password, message.receiver, message.theme, message.body)
    if check:
        return {"message": "Сообщение отправлено"}
    else:
        return {"message": "Ошибка"}

uvicorn.run(app, host=run_host, port=run_port)