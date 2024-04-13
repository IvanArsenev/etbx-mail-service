import uvicorn, jwt

from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from PIL import Image
from pathlib import Path
from passlib.context import CryptContext

from classes import *
from database_api import *
from config import *



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

webdrivers_list = {}




def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def crop_center(img, new_width, new_height):
    width, height = img.size
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2
    img_cropped = img.crop((left, top, right, bottom))
    return img_cropped


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def convert_data(data):
    if isinstance(data, str):
        try:
            data = datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            data = datetime.strptime(data, "%d-%m-%Y")
    if data.time() != datetime.min.time():
        formatted_datetime = data.strftime("%H:%M %d.%m.%Y")
    else:
        formatted_datetime = data.strftime("%d.%m.%Y")
    return formatted_datetime


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Вы не авторизованы!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except jwt.PyJWTError: raise credentials_exception
    data = get_user(username)[1][0]
    try:
        img = Image.open(f'avatars/{data[0]}.png')
        avatar = True
    except:
        avatar = False
    user = {
        "id": data[0],
        "Имя": data[1],
        "Фамилия": data[2],
        "Дата рождения": convert_data(data[3]),
        "Пол": data[4],
        "Логин": data[5],
        "Аватар": avatar,
        "token": token
    }
    return user




@app.post("/register")
async def perform_register(request: RegistrationRequest):
    try:
        if get_user(request.mail)[0]:
            return HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
        else:
            hashed_password = get_password_hash(request.password)
            access_token = create_access_token(data={"sub": request.mail})
            db_request(f'INSERT INTO users (name, surname, birthday, gender, mail, phone_num, password, token) VALUES ("{request.name}", "{request.surname}", "{request.birthday}", "{request.gender}", "{request.mail}", "{request.phone_num}", "{hashed_password}", "{access_token}")')
            return {"Token": access_token}
    except:
        raise HTTPException(status_code=400, detail="Ошибка при регистрации")


@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if user[1][0][9] == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ваш аккаунт забанен! Обратитесь в службу поддержки для разбана",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин",
            headers={"WWW-Authenticate": "Bearer"},
        )
    hashed_password = user[1][0][7]
    if not verify_password(form_data.password, hashed_password):
        if int(user[1][0][10]) < 10:
            db_request(f"UPDATE users SET enter_count = enter_count + 1 WHERE id = {user[1][0][0]}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            db_request(f"UPDATE users SET banned = True WHERE id = {user[1][0][0]}")
            db_request(f'INSERT INTO disabled_tokens (token) VALUES ("{user[1][0][8]}")')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ваш аккаунт забанен! Обратитесь в службу поддержки для разбана",
                headers={"WWW-Authenticate": "Bearer"},
            )
    token = user[1][0][8]
    db_request(f"UPDATE users SET enter_count = 0 WHERE id = {user[1][0][0]}")
    db_request(f'DELETE FROM disabled_tokens WHERE token = "{token}"')
    return {"Token": token}


@app.get("/users/{id}/avatar")
async def read_user_avatar(id: str, current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['Логин']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    avatar_path = Path(f'avatars/{id}.png')
    if not avatar_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Изображение не найдено")
    return FileResponse(avatar_path)


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['Логин']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


@app.get("/users/{id}")
async def read_users_id(id: str, current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['Логин']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        data = get_user_by_id(id)[1][0]
        try:
            img = Image.open(f'avatars/{data[0]}.png')
            avatar = True
        except:
            avatar = False
        user = {
            "Имя": data[1],
            "Фамилия": data[2],
            "Дата рождения": convert_data(data[3]),
            "Пол": data[4],
            "Логин": data[5],
            "Аватар": avatar,
        }
        return user
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Пользователь не найден!")


@app.get("/users/")
async def read_users(page: int = 1, page_size: int = 10, current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['Логин']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    users = get_users_db()
    total_users = len(users)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    users_on_page = users[start_index:end_index]
    formatted_users = []
    for user in users_on_page:
        try:
            img = Image.open(f'avatars/{user[0]}.png')
            avatar = True
        except:
            avatar = False
        if user[4] == 'М': gender = 'Мужской'
        else: gender = 'Женский'
        try:
            flag = user[6][0]
            phone = user[6]
        except:
            phone = 'Отсутствует'
        formatted_user = {
            "id": user[0],
            "Имя": user[1],
            "Фамилия": user[2],
            "Дата рождения": convert_data(user[3]),
            "Пол": gender,
            "Логин": user[5],
            "Номер телефона": phone,
            "Аватар": avatar
        }
        formatted_users.append(formatted_user)
    return {"total_users": total_users, "users": formatted_users}


@app.put("/edit_avatar")
async def edit_avatar(avatar: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
            save_path = Path(f"./avatars/{current_user['id']}.png")
            img.save(save_path, format="PNG")
        return {"message": "Аватар успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке файла: {str(e)}")


@app.put("/edit")
async def edit_me(updated_profile: EditProfile, current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    fields_to_update = {}
    if updated_profile.name is not None: fields_to_update['name'] = updated_profile.name
    if updated_profile.surname is not None: fields_to_update['surname'] = updated_profile.surname
    if updated_profile.birthday is not None: fields_to_update['birthday'] = updated_profile.birthday
    if updated_profile.gender is not None: fields_to_update['gender'] = updated_profile.gender
    if updated_profile.mail is not None: fields_to_update['mail'] = updated_profile.mail
    if updated_profile.phone_num is not None: fields_to_update['phone_num'] = updated_profile.phone_num
    if updated_profile.password is not None: fields_to_update['password'] = get_password_hash(updated_profile.password)
    try:
        update_query = 'UPDATE users SET '
        update_query += ', '.join([f'{field}="{value}"' for field, value in fields_to_update.items()])
        update_query += f' WHERE mail="{current_user["Логин"]}"'
        db_request(update_query)
        return {"message": "Профиль успешно обновлен"}
    except:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении профиля")


@app.post("/logout")
async def logout_me(current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = current_user['token']
    db_request(f'INSERT INTO disabled_tokens (token) VALUES ("{token}")')
    return {"message": "Вы успешно вышли!"}


@app.post("/send")
async def send_message(message: MailModel, current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sender = current_user["Логин"]
    recipients = message.reciever
    subject = message.theme
    body = message.body
    
    # Тут отправляем почту

    db_request(f'INSERT INTO mails (theme, body, sender, reciever, time) VALUES ("{subject}", "{body}", "{sender}", "{recipients}", "{datetime.now()}")')
    return {"message": "Сообщение отправлено!"}


@app.get("/messages/get/sended")
async def get_messages_sended(current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    messages_sended = get_messages_sended_db(current_user['Логин'])
    formatted_messages = []
    for message in messages_sended:
        formatted_message = {
            "id": message[0],
            "Тема": message[1],
            "Сообщение": message[2],
            "Отправитель": message[3],
            "Получатель": message[4],
            "Время отправки": convert_data(message[5])
        }
        formatted_messages.append(formatted_message)
    return {"messages": formatted_messages}


@app.get("/messages/get/recieved")
async def get_messages_recieved(current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    messages_recieved = get_messages_recieved_db(current_user['Логин'])
    formatted_messages = []
    for message in messages_recieved:
        formatted_message = {
            "id": message[0],
            "Тема": message[1],
            "Сообщение": message[2],
            "Отправитель": message[3],
            "Получатель": message[4],
            "Время получения": convert_data(message[5])
        }
        formatted_messages.append(formatted_message)
    return {"messages": formatted_messages}




uvicorn.run(app, host=run_host, port=run_port)