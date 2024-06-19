import React, { ChangeEvent, DOMElement, useRef, useState } from 'react';
import { Navigate } from 'react-router-dom';

import styles from './CreateMessage.module.scss';

const CreateMessage: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);

    const textArea = useRef<HTMLTextAreaElement>();

    if (isAuth) {
      return <Navigate to="/" />;
    }

    const handleTextChange = (event: ChangeEvent) => {
      event.target.setAttribute('style', `height: 0px`);
      event.target.setAttribute('style', `height: ${event.target.scrollHeight}px`);
    }

    return (
      <>
        <div className={styles.createMessage}>
          <div className={styles.emodjiButton}>

          </div>
          <textarea name="messageField" id="messageField"
            className={styles.inputText} placeholder={'Сообщение'}
            onChange={(e) => handleTextChange(e)}
          >
          </textarea>
          <div className={styles.attachButton}>
          </div>
          <div className={styles.sendButton}>
          </div>
        </div>
      </>
    );
};
export default CreateMessage;
