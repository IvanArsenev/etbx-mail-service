import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import styles from './Registration.module.scss';

const Login: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);
    const [passwordStrength, setPasswordStrength] = useState<number>(0);
    const [colorLoad, setLoaderColor] = useState<string>('rgb(255, 0, 0)');
    const [mainPassword, setMainPassword] = useState<string>('');
    const [passwordIsValid, setPasswordValidation] = useState<boolean>(false);
    const [passwordError, setPasswordError] = useState<string>('none');
    const [copyPassword, setCopyPassword] = useState<string>('');
    const [passwordsAreSame, setSamenest] = useState<string>('none');

    const baseSymbols = 'qwertyuiopasdfghjklzxcvbnm';
    const bigSymbols = 'QWERTYUIOPASDFGHJKLZXCVBNM';
    const russianSymbols = 'йцукенгшщзхъфывапролджэячсмитьбюё';
    const russianBigSymbols = 'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ';
    const extraSymbols = '`~1234567890-=!@#$%^&*()_+"№;%:?[]{},.<>/|\\ ';
    const totalSymbols = baseSymbols + bigSymbols + russianSymbols + russianBigSymbols + extraSymbols;

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
        if (!passwordIsValid) {
            setPasswordError('inline-block');
        }
        else {
            setPasswordError('none');
        }
    }, [passwordIsValid]);

    if (isAuth) {
        return <Navigate to="/" />;
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

    return (
        <div className={styles.container}>
            <div className={styles.wall}>
                <div className={styles.mainBlock}>
                    <div className={styles.block}>
                        <div className={`${styles.label}`}>
                            Электронная почта
                        </div>
                        <input placeholder='myemail@example.etb' type="text" className={`${styles.inputLike}`} />
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
                    <div id='submitButton' className={`${styles.submitButton} ${styles.buttonInactive}`}>
                        Зарегистрироваться
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Login;
