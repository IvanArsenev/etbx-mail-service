import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import styles from './Registration.module.scss';
import { registerUser, UserData } from '../../api/RegistrationApi/index.ts';
import { checkAuth } from '../../utils.ts';

const Registration: React.FC = () => {
    const navigate = useNavigate();

    const [passwordStrength, setPasswordStrength] = useState<number>(0);
    const [colorLoad, setLoaderColor] = useState<string>('rgb(255, 0, 0)');
    const [mainPassword, setMainPassword] = useState<string>('');
    const [passwordIsValid, setPasswordValidation] = useState<boolean>(false);
    const [passwordError, setPasswordError] = useState<string>('none');
    const [copyPassword, setCopyPassword] = useState<string>('');
    const [passwordsAreSame, setSamenest] = useState<string>('none');
    const [birthdayIsCorrect, setBirthdayIsCorrect] = useState<boolean>(false);
    const [allFieldsFilled, setAllFieldsFilled] = useState<boolean>(false);

    const [name, setName] = useState<string>('');
    const [surname, setSurname] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [birthday, setBirthday] = useState<string>(Date());
    const [gender, setGender] = useState<string>('М');
    const [phone, setPhone] = useState<string>('+7');

    const baseSymbols = 'qwertyuiopasdfghjklzxcvbnm';
    const bigSymbols = 'QWERTYUIOPASDFGHJKLZXCVBNM';
    const russianSymbols = 'йцукенгшщзхъфывапролджэячсмитьбюё';
    const russianBigSymbols = 'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ';
    const extraSymbols = '`~1234567890-=!@#$%^&*()_+"№;%:?[]{},.<>/|\\ ';
    const totalSymbols = baseSymbols + bigSymbols + russianSymbols + russianBigSymbols + extraSymbols;

    useEffect(() => {
        const verifyAuth = async () => {
          const user = await checkAuth();
          if (user?.message !== 'Войдите в систему!' && user !== null) {
            navigate('/users');
          }
        };
    
        verifyAuth();
    }, [navigate]);

    useEffect(() => {
        if (mainPassword === copyPassword) {
            setSamenest('none');
        }
        else {
            setSamenest('inline-block');
        }

        setPasswordValidation(checkIfPasswordIsValid());

    }, [mainPassword, copyPassword]);

    useEffect(() => {
        console.log(new Date(birthday) >= new Date('01.01.1910'), new Date(birthday) < new Date());
        if (new Date(birthday) >= new Date('01.01.1910') && new Date(birthday) < new Date()) {
            setBirthdayIsCorrect(true);
        }
        else {
            setBirthdayIsCorrect(false);
        }
    }, [birthday])

    useEffect(() => {
        if (!passwordIsValid) {
            setPasswordError('inline-block');
        }
        else {
            setPasswordError('none');
        }
    }, [passwordIsValid]);

    useEffect(() => {
        setAllFieldsFilled(name && surname && email && birthday && gender && mainPassword);
    }, [name, surname, email, birthday, gender, mainPassword]);

    const handleSend = () => {
        const dataBody: UserData = {
            name: name,
            surname: surname,
            birthday: formatDate(birthday),
            gender: gender,
            mail: email,
            phone_num: formatPhone(phone),
            password: mainPassword,
        }
        const responce = registerUser(dataBody);
        if (responce !== null) {
            navigate('/users');
        }
    }

    const setBasePhone = (target, phone_value: string) => {
        const pattern = ['+', '7', ' ', '(', '0123456789', '0123456789', '0123456789', ')', ' ', '0123456789', '0123456789', '0123456789', ' ', '0123456789', '0123456789', '-', '0123456789', '0123456789'];

        let new_phone = '';
        let k = 0;
        for (let i = 0; i < Math.min(phone_value.length, pattern.length); i++) {
            const letter = phone_value[i];
            if (!pattern[k].includes(letter)) {
                new_phone += pattern[k][0];
                k += 1;
                if (k < pattern.length) {
                    let ok = false;
                    if (!pattern[k].includes(letter)) {
                        new_phone += pattern[k][0];
                    }
                    else {
                        new_phone += letter;
                        ok = true;
                    }
                    k += 1;
                    if (k < pattern.length && !ok) {
                        if (pattern[k].includes(letter)) {
                            new_phone += letter;
                        }
                    }
                }
            }
            else {
                new_phone += phone_value[i];
            }
            k += 1;
        }

        target.value = new_phone;
        setPhone(new_phone);
    }

    const passwordSecond = (password:string) => {
        setCopyPassword(password);
    }

    const checkIfPasswordIsValid = () => {
        let flag = true;

        for (let i = 0; i < mainPassword.length; i++) {
            const letter = mainPassword[i];
            if (!totalSymbols.includes(letter)) {
               flag = false; 
            }
        }

        if (mainPassword.length < 8) {
            flag = false;
        }

        return flag;
    }

    const passwordHardness = (password:string) => {
        const length = password.length;
        let baseKoef = 0;
        let bigKoef = 0;
        let russianKoef = 0;
        let rusBigKoef = 0;
        let extraKoef = 0;

        setMainPassword(password);
        
        for (let i = 0; i < length; i++) {
            const letter:string = password[i];
            if (baseSymbols.includes(letter)) {
                baseKoef = 1;
            }
            if (bigSymbols.includes(letter)) {
                bigKoef = 1;
            }
            if (russianSymbols.includes(letter)) {
                russianKoef = 1;
            }
            if (russianBigSymbols.includes(letter)) {
                rusBigKoef = 1;
            }
            if (extraSymbols.includes(letter)) {
                extraKoef = 1;
            }
        }

        let symbolsAscii = baseKoef * baseSymbols.length +
        bigKoef * bigSymbols.length + russianKoef * russianSymbols.length +
        rusBigKoef * russianBigSymbols.length + extraKoef * extraSymbols.length;

        let totalLength = baseSymbols.length + bigSymbols.length + 
        russianSymbols.length + russianBigSymbols.length + extraSymbols.length;

        const strength = Math.min(1, (symbolsAscii*length) / (totalLength*20)) * 100;

        if (strength >= 66.666) {
            setLoaderColor('rgb(0, 250, 50)');
        }
        else if (strength >= 33.333) {
            setLoaderColor('rgb(255, 200, 0)');
        }
        else {
            setLoaderColor('rgb(255, 0, 0)');
        }

        setPasswordStrength(strength);
    }

    const formatDate = (date:string): string => {
        const year = date.split('-')[0];
        const month = date.split('-')[1];
        const day = date.split('-')[2];
        return `${day}-${month}-${year}`;
    }

    const formatPhone = (phone:string): string => {
        const newPhone = phone.replace('+', '').replace(' ', '').replace('(', '').replace(')', '').replace('-', '');
        return newPhone;
    }

    return (
        <div className={styles.container}>
            <div className={styles.wall}>
                <div className={styles.mainBlock}>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Имя
                        </div>
                        <input placeholder='Введите имя' type="text" className={`${styles.inputLike}`}
                        onChange={(e) => setName(e.target.value)} />
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Фамилия
                        </div>
                        <input placeholder='Введите фамилию' type="text" className={`${styles.inputLike}`}
                        onChange={(e) => setSurname(e.target.value)} />
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Дата рождения
                        </div>
                        <input type="date" className={`${styles.inputLike}`}
                        onChange={(e) => setBirthday(e.target.value)} />
                        <div style={{display: birthdayIsCorrect ? 'none' : ''}} className={`${styles.error}`}>
                            Дата рождения не может быть в будущем. Дата рождения должна быть не раньше 1 января 1910 года.
                        </div>
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Пол
                        </div>
                        <div>
                            <input type="radio" name="gender" value="male" className={`${styles.inputRadioLike}`}
                            onChange={(e) => setGender(e.target.value)} /> Мужской
                        </div>
                        <div>
                            <input type="radio" name="gender" value="female" className={`${styles.inputRadioLike}`}
                            onChange={(e) => setGender(e.target.value)} /> Женский
                        </div>
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Электронная почта
                        </div>
                        <input placeholder='myemail' type="text" className={`${styles.inputLike}`}
                        onChange={(e) => setEmail(e.target.value)} />
                        <div style={{display: 'none'}} className={`${styles.error}`}>
                            Кажется, введён некорректный e-mail
                        </div>
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Номер телефона
                        </div>
                        <input placeholder='+7 (900) 850 34-44' type="phone" className={`${styles.inputLike}`}
                        onChange={(e) => setBasePhone(e.target, e.target.value)} />
                        <div style={{display: 'none'}} className={`${styles.error}`}>
                            Кажется, введён некорректный e-mail
                        </div>
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Пароль
                        </div>
                        <input placeholder='Придумайте пароль' type="password" className={`${styles.inputLike}`} 
                        onChange={e => passwordHardness(e.target.value)}/>
                        <div className={`${styles.loaderBack}`}>
                            <div style={{width: `${passwordStrength}%`, backgroundColor: `${colorLoad}`}} className={`${styles.loader}`}>
                            </div>
                        </div>
                        <div style={{display: passwordError}} className={`${styles.error}`}>
                            Пароль должен быть не менее 8 символов в длину и может содержать только символы кирилицы, латинского алфавита, цифр, спец-символы.
                        </div>
                    </div>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Повторите пароль
                        </div>
                        <input placeholder='Повторите пароль' type="password" className={`${styles.inputLike}`} 
                        onChange={e => passwordSecond(e.target.value)}/>
                        <div style={{display: passwordsAreSame}} className={`${styles.error}`}>
                            Пароли не совпадают
                        </div>
                    </div>
                    <div style={{display: 'flex', flexDirection: 'row', width: '100%'}}>
                        <div id='submitButton' className={`${styles.submitButton}`} onClick={handleSend}>
                            Зарегистрироваться
                        </div>
                        <div id='loginGo' className={`${styles.submitButton} ${styles.buttonInactive}`} onClick={() => { navigate('/login') }}>
                            Войти
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Registration;
