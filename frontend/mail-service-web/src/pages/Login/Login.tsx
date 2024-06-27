import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import styles from './Login.module.scss';
import { checkAuth } from '../../utils.ts';
import { UserLogData, loginUser } from '../../api/LoginApi/index.ts';

const Login: React.FC = () => {
    const navigate = useNavigate();

    const [mainPassword, setMainPassword] = useState<string>('');
    const [email, setEmail] = useState<string>('');

    useEffect(() => {
        const verifyAuth = async () => {
          const user = await checkAuth();
          if (user?.message !== 'Войдите в систему!' && user !== null) {
            navigate('/users');
          }
        };
    
        verifyAuth();
    }, [navigate]);

    const handleSend = () => {
        const dataBody: UserLogData = {
            email: email,
            password: mainPassword,
        }
        const responce = loginUser(dataBody);
        if (responce !== null) {
            navigate('/users');
        }
    }

    return (
        <div className={styles.container}>
            <div className={styles.wall}>
                <div className={styles.mainBlock}>
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
                            Пароль
                        </div>
                        <input placeholder='Придумайте пароль' type="password" className={`${styles.inputLike}`} 
                        onChange={e => setMainPassword(e.target.value)}/>
                    </div>
                    <div id='submitButton' className={`${styles.submitButton}`} onClick={handleSend}>
                        Войти
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Login;
