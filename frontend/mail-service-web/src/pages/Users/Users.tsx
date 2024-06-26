import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

import { UserObject, UserResponce } from './constants';

import styles from './Users.module.scss';
import { GetAvatar, UsersAll } from '../../api/UserApi';
import Spinner from '../Spinner/Spinner';

const Users: React.FC = () => {
    const [getStatus, setGetStatus] = useState<boolean>(false);
    const [usersResp, setUsersResp] = useState<UserResponce>({ total_users: 0, users: [] });
    const [usersAvatars, setUsersAvatars] = useState<any[]>([]);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const fetchedUsers = await UsersAll();
                await setUsersResp(fetchedUsers);
                await setGetStatus(true);
                // чего
                // let newAvs:any[] = [];
                // for (let i = 0; i < fetchedUsers.total_users; i++) {
                //     if (fetchedUsers.users[i].Аватар !== null) {
                //         newAvs.push(await GetAvatar(fetchedUsers.users[i].Аватар))
                //     }
                //     else {
                //         newAvs.push('');
                //     }
                // }
                // setUsersAvatars(newAvs);
            } catch (error) {
                setGetStatus(true);
                console.error('Error fetching users:', error);
            }
        };

        fetchUsers();
    }, []);
    
    const handleChoose = (event: any, id: number) => {
        const userBlocks = document.querySelectorAll(`.${styles.userBlock}`);

        // Удаление класса choosed у всех элементов
        userBlocks.forEach((block) => {
            block.classList.remove(styles.choosed);
        });
        
        const userBlock = event.currentTarget;
        console.log(userBlock);
        const isChoosed = userBlock.classList.contains(styles.choosed);
        if (!isChoosed) {
            const firstChild = userBlock.querySelector(`#${userBlock.id}_click`);
        
            const rect = userBlock.getBoundingClientRect();
            const offsetX = event.clientX - rect.left - rect.width/2;
            const offsetY = event.clientY - rect.top - rect.height/2;
            console.log(offsetX, offsetY);
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
        window.location.pathname = `/users/${id}`;
        // return <Navigate to={} />;
    };

    return (
        <>
            <div className={styles.wall}>
                {usersResp.users.map((user: UserObject, index: number) => (
                    <div 
                        style={{zIndex: usersResp.total_users - index}}
                        id={`user_${user.id}`}
                        onClick={ (e) => handleChoose(e, user.id) }
                        className={`${styles.userBlock}`}
                    >
                        <img src="" alt="" className={styles.userAvatar} />
                        <div className={styles.userTop}>
                            <div className={styles.userName}>
                                {user.Фамилия} {user.Имя}
                            </div>
                            <div className={styles.userLastDate}>
                                {user.Почта}
                            </div>
                            {/* <div className={styles.userLastTheme}>
                                {user.lastTheme}
                            </div> */}
                        </div>
                        <div style={{zIndex: -100}} id={`user_${user.id}_click`} className={styles.click}></div>
                    </div>
                ))}
                <Spinner display={!getStatus} />
            </div>
        </>
    );
};
export default Users;
