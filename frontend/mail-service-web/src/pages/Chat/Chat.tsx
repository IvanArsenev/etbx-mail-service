import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';

import styles from './Chat.module.scss';
import { messages } from './constants.ts';

const CreateMessage = React.lazy(async () => await import('../../pages/CreateMessage/CreateMessage.tsx'));

const Users: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);
    const userId = 1;

    if (isAuth) {
      return <Navigate to="/" />;
    }

    return (
      <div style={{display: 'flex', flexDirection: 'column', width: '100%'}}>
        <div className={styles.chat}>
          {
            messages.slice(0).reverse().map((message, index) => {
              let prevUserId: number | null = null;
              let nextUserId: number | null = null;

              if (messages.length - index - 1 + 1 < messages.length) {
                nextUserId = messages[messages.length - index - 1 + 1].authorId;
              }
              if (messages.length - index - 1 - 1 >= 0) {
                prevUserId = messages[messages.length - index - 1 - 1].authorId;
              }

              const isFirst = message.authorId !== prevUserId;
              const isLast = message.authorId !== nextUserId;
              
              return (
                <div className={`${styles.messageBlock} ${userId === message.authorId ? styles.myMessageBlock : ''}`}>
                  <div className={styles.avatarBlock}>
                    {isLast ? <img src="" alt="" className={styles.userAvatar} /> : <></>}
                  </div>
                  <div className={`${styles.message} ${isFirst ? styles.firstMessage : ''}
                  ${isLast ? styles.lastMessage : ''} ${userId === message.authorId ? styles.myMessage : ''}`}>
                    <div className={styles.content}>
                      {message.content}
                    </div>
                    <div className={styles.date}>
                      {message.createdTime}
                    </div>
                  </div>
                </div>
              )
            })
          }
        </div>
        <CreateMessage />
      </div>
    );
};
export default Users;
