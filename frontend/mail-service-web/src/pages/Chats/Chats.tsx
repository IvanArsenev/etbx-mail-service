import React, { useState } from 'react';
import { Navigate, useParams } from 'react-router-dom';

import UserAuth, { themes } from './constants.ts';

import styles from './Chats.module.scss';

const Chats: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);

    const { id } = useParams<{ id: string }>();

    if (themes.length <= parseInt(id ?? '0')) {
        return <Navigate to="/users" />;
    }

    if (isAuth) {
        return <Navigate to="/" />;
    }

    const onFinish = ({ username, password }: UserAuth): void => {
        if (!isAuth) {
        }
    };

    const handleChoose = (event): void => {
        const themeBlocks = document.querySelectorAll(`.${styles.themeBlock}`);

        // Удаление класса choosed у всех элементов
        themeBlocks.forEach((block) => {
            block.classList.remove(styles.choosed);
        });
        
        const themeBlock = event.currentTarget;
        const isChoosed = themeBlock.classList.contains(styles.choosed);
        if (!isChoosed) {
            const firstChild = themeBlock.querySelector(`#${themeBlock.id}_click`);
        
            const rect = themeBlock.getBoundingClientRect();
            const offsetX = event.clientX - rect.left - rect.width/2;
            const offsetY = event.clientY - rect.top - rect.height/2;

            let percentX = offsetX * 100 / rect.width;
            let percentY = offsetY * 100 / rect.height;

            firstChild.style.top = `${percentY+50}%`;
            firstChild.style.left = `${percentX+50}%`;
            firstChild.style.width = "250%";
            firstChild.style.backgroundColor = "rgb(241, 238, 255)";
            setTimeout(() => {
                themeBlock.classList.toggle(styles.choosed);
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
        <div className={styles.wall}>
            {themes[parseInt(id ?? '0')].map((theme, index) => (
                <div style={{zIndex: themes.length - theme.id}} id={`theme_${theme.id}`} onClick={ (e) => handleChoose(e) } className={`${styles.themeBlock}`}>
                    <div id={`theme_${theme.id}_click`} className={styles.click}></div>
                    <img src="" alt="" className={styles.themeAvatar} />
                    <div className={styles.themeTop}>
                        <div className={styles.themeName}>
                            {theme.name}
                        </div>
                        <div className={styles.themeLastDate}>
                            {theme.lastMessageDate}
                        </div>
                        <div className={styles.themeLastTheme}>
                            {theme.lastMail}
                        </div>
                    </div>
                </div>
            ))}
            
        </div>
    );
};
export default Chats;
