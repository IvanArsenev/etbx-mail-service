import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import styles from './Chats.module.scss';
import { GetThemes } from '../../api/ThemesApi/index.ts';
import Chat from '../Chat/Chat.tsx';

const Spinner = React.lazy(async () => await import('../Spinner/Spinner.tsx'));

const Chats: React.FC = () => {
    const [getStatus, setGetStatus] = useState<boolean>(false);
    const [chatsResp, setChatsResp] = useState<string[]>([]);

    const [theme, setTheme] = useState<string | null>(null);

    const { id } = useParams<{ id: string }>();

    const navigate = useNavigate();

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                if (id) {
                    const fetched = await GetThemes(id ?? '');
                    console.log(fetched)
                    setChatsResp(fetched?.themes ?? []);
                    setGetStatus(true);

                    localStorage.setItem('mailUserId', id);
                }
                else {
                    navigate('/users')
                }
            } catch (error) {
                setGetStatus(true);
                console.error('Error fetching:', error);
            }
        };

        fetchUsers();
    }, [id]);

    const handleChoose = (event: string): void => {
        // const themeBlocks = document.querySelectorAll(`.${styles.themeBlock}`);

        localStorage.setItem('mailChoosedTheme', event);
        // console.log(event.currentTarget.id.split('_')[1]);
        setTheme(event);

        // Удаление класса choosed у всех элементов
        // themeBlocks.forEach((block) => {
        //     block.classList.remove(styles.choosed);
        // });
        
        // const themeBlock = event.currentTarget;
        // const isChoosed = themeBlock.classList.contains(styles.choosed);
        // if (!isChoosed) {
        //     const firstChild = themeBlock.querySelector(`#${themeBlock.id}_click`);
        
        //     const rect = themeBlock.getBoundingClientRect();
        //     const offsetX = event.clientX - rect.left - rect.width/2;
        //     const offsetY = event.clientY - rect.top - rect.height/2;

        //     let percentX = offsetX * 100 / rect.width;
        //     let percentY = offsetY * 100 / rect.height;

        //     firstChild.style.top = `${percentY+50}%`;
        //     firstChild.style.left = `${percentX+50}%`;
        //     firstChild.style.width = "250%";
        //     firstChild.style.backgroundColor = "rgb(241, 238, 255)";
        //     setTimeout(() => {
        //         themeBlock.classList.toggle(styles.choosed);
        //         firstChild.style.width = "0%";
        //         firstChild.style.display = 'none';
        //         firstChild.style.backgroundColor = "rgb(195, 182, 255)";
        //         setTimeout(() => {
        //             firstChild.style.display = 'block';
        //         }, 500);
        //     }, 600);
        // }
    };

    return (
        <>
        <div className={styles.wall}>
            {chatsResp.map((theme, index) => (
                <div style={{zIndex: chatsResp.length - index}} id={`${index}`} onClick={ (e) => handleChoose(theme) } className={`${styles.themeBlock}`}>
                    <div id={`${index}`} className={styles.click} onClick={ (e) => handleChoose(theme) } ></div>
                    <img src="" alt="" className={styles.themeAvatar} onClick={ (e) => handleChoose(theme) } />
                    <div className={styles.themeTop} onClick={ (e) => handleChoose(theme) } >
                        <div className={styles.themeName} onClick={ (e) => handleChoose(theme) } >
                            {theme}
                        </div>
                        {/* <div className={styles.themeLastDate}>
                            {theme.lastMessageDate}
                        </div>
                        <div className={styles.themeLastTheme}>
                            {theme.lastMail}
                        </div> */}
                    </div>
                </div>
            ))}
            <Spinner display={!getStatus} />
        </div>
        <Chat userId={id ?? null} theme={theme ?? null}/>
        </>
    );
};
export default Chats;
