import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

import styles from './Chat.module.scss';
import { GetMessages } from '../../api/MessagesApi/index.ts';
import Spinner from '../Spinner/Spinner.tsx';
import { UserObject } from '../Users/constants.ts';
import { checkAuth } from '../../utils.ts';
import { Message } from './constants.ts';

interface IProps {
  userId: string | null;
  theme: string | null;
}

const CreateMessage = React.lazy(async () => await import('../../pages/CreateMessage/CreateMessage.tsx'));

const Users: React.FC<IProps> = (items: IProps) => {
  const [getStatus, setGetStatus] = useState<boolean>(false);
  const [chatResp, setChatResp] = useState<Message[]>([]);

  const [user, setUser] = useState<UserObject | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsers = async () => {
        try {
          if (localStorage.getItem('mailChoosedTheme')) {
            const fetched = await GetMessages(items.userId ?? '', items.theme ?? '');
              
            setChatResp(fetched ?? []);
            console.log('messages', fetched);
            setGetStatus(true);
          }
        } catch (error) {
          setGetStatus(true);
          console.error('Error fetching:', error);
        }
    };

    fetchUsers();
  }, [items]);

  useEffect(() => {
    const verifyAuth = async () => {
      const user = await checkAuth();
      setUser(user);
    };

    verifyAuth();
  }, [navigate]);
  
  return (
    <div style={{display: 'flex', flexDirection: 'column', width: '100%'}}>
      <div className={styles.chat}>
        <Spinner display={!getStatus} />
        {
          chatResp.slice(0).reverse().map((message, index) => {
            let prevUserId: string | null = null;
            let nextUserId: string | null = null;

            if (chatResp.length - index - 1 + 1 < chatResp.length) {
              nextUserId = chatResp[chatResp.length - index - 1 + 1].sender;
            }
            if (chatResp.length - index - 1 - 1 >= 0) {
              prevUserId = chatResp[chatResp.length - index - 1 - 1].sender;
            }

            const isFirst = message.sender !== prevUserId;
            const isLast = message.sender !== nextUserId;
            
            return (
              <div className={`${styles.messageBlock} ${user?.Почта === message.sender ? styles.myMessageBlock : ''}`}>
                <div className={styles.avatarBlock}>
                  {isLast ? <img src="" alt="" className={styles.userAvatar} /> : <></>}
                </div>
                <div className={`${styles.message} ${isFirst ? styles.firstMessage : ''}
                ${isLast ? styles.lastMessage : ''} ${user?.Почта === message.sender ? styles.myMessage : ''}`}>
                  <div className={styles.content}>
                    {message.body}
                  </div>
                  <div className={styles.date}>
                    {message.received_time}
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
