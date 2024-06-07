import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';

import UserAuth, { users } from './constants.ts';

import styles from './Login.module.scss';

const Login: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);

    if (isAuth) {
        return <Navigate to="/" />;
    }

    const onFinish = ({ username, password }: UserAuth): void => {
        if (!isAuth) {
        }
    };

    const handleChoose = (event): void => {
        const userBlocks = document.querySelectorAll(`.${styles.userBlock}`);

        // Удаление класса choosed у всех элементов
        userBlocks.forEach((block) => {
            block.classList.remove(styles.choosed);
        });
        
        const userBlock = event.currentTarget;
        const isChoosed = userBlock.classList.contains(styles.choosed);
        if (!isChoosed) {
            const firstChild = userBlock.querySelector(`#${userBlock.id}_click`);
        
            const rect = userBlock.getBoundingClientRect();
            const offsetX = event.clientX - rect.left - rect.width/2;
            const offsetY = event.clientY - rect.top - rect.height/2;

            let percentX = offsetX * 100 / rect.width;
            let percentY = offsetY * 100 / rect.height;

            firstChild.style.top = `${percentY+50}%`;
            firstChild.style.left = `${percentX+50}%`;
            firstChild.style.width = "250%";
            firstChild.style.backgroundColor = "rgb(241, 238, 255)";
            setTimeout(() => {
                userBlock.classList.toggle(styles.choosed);
                firstChild.style.width = "0%";
                firstChild.style.display = 'none';
                firstChild.style.backgroundColor = "rgb(195, 182, 255)";
                setTimeout(() => {
                    firstChild.style.display = 'block';
                }, 500);
            }, 600);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.wall}>
                {users.map((user, index) => (
                    <div style={{zIndex: users.length - user.id}} id={`user_${user.id}`} onClick={ (e) => handleChoose(e) } className={`${styles.userBlock}`}>
                        <div id={`user_${user.id}_click`} className={styles.click}></div>
                        <img src="" alt="" className={styles.userAvatar} />
                        <div className={styles.userTop}>
                            <div className={styles.userName}>
                                {user.username}
                            </div>
                            <div className={styles.userLastDate}>
                                {user.lastDate}
                            </div>
                            <div className={styles.userLastTheme}>
                                {user.lastTheme}
                            </div>
                        </div>
                    </div>
                ))}
                
            </div>
            <div className={styles.chat}>
            </div>
        </div>
    );
};
export default Login;
