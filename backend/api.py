import uvicorn, jwt

from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from classes import *
from database_api import *
from config import *

app = FastAPI()

webdrivers_list = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def convert_data(data):
    if isinstance(data, str):
        try: data = datetime.strptime(data, "%d-%m-%Y %H:%M:%S.%f")
        except ValueError: data = datetime.strptime(data, "%d-%m-%Y")
    if data.time() != datetime.min.time(): formatted_datetime = data.strftime("%H:%M %d.%m.%Y")
    else: formatted_datetime = data.strftime("%d.%m.%Y")
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
    user = {
        "Имя": data[1],
        "Фамилия": data[2],
        "Дата рождения": convert_data(data[3]),
        "Пол": data[4],
        "Логин": data[5],
        "token": token
    }
    return user



@app.post("/register")
async def perform_register(request: RegistrationRequest):
    try:
        if get_user(request.mail)[0]:
            return HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
        else:
            access_token = create_access_token(data={"sub": request.mail})
            db_request(f'INSERT INTO users (name, surname, birthday, gender, mail, phone_num, password, token) VALUES ("{request.name}", "{request.surname}", "{request.birthday}", "{request.gender}", "{request.mail}", "{request.phone_num}", "{request.password}", "{access_token}")')
            return {"Token": access_token}
    except:
        raise HTTPException(status_code=400, detail="Ошибка при регистрации")


@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if not login_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = get_user(form_data.username)[1][0][8]
    db_request(f'DELETE FROM disabled_tokens WHERE token = "{token}"')
    return {"Token": token}


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    if not current_user or unauthorised_token(current_user['token']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


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
    if updated_profile.password is not None: fields_to_update['password'] = updated_profile.password
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
            "Время отправки": message[5]
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
            "Время получения": message[5]
        }
        formatted_messages.append(formatted_message)
    return {"messages": formatted_messages}




if __name__ == "__main__":
    uvicorn.run(app, host=run_host, port=run_port)