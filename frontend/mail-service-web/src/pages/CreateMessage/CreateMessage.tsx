import React, { ChangeEvent, DOMElement, useRef, useState } from 'react';
import { SendMessage } from '../../api/MessagesApi/index.ts';

import styles from './CreateMessage.module.scss';

interface IProps {
  userId: string,
  theme: string,
  sendMsg: () => void
}

const CreateMessage: React.FC<IProps> = (items:IProps) => {
    const [ messageText, sendMessageText] = useState<string | null>(null);

    const textArea = useRef<HTMLTextAreaElement>();

    const handleTextChange = (event: ChangeEvent) => {
      event.target.setAttribute('style', `height: 0px`);
      event.target.setAttribute('style', `height: ${event.target.scrollHeight}px`);
      
      sendMessageText(textArea.current.value);
    }

    const handleSendMessage = () => {
      SendMessage(items.userId, items.theme, messageText);
      textArea.current.value = '';
      items.sendMsg();
    }

    return (
      <>
        <div className={styles.createMessage}>
          <div className={styles.emodjiButton}>

          </div>
          <textarea name="messageField" id="messageField"
            className={styles.inputText} placeholder={'Сообщение'}
            onChange={(e) => handleTextChange(e)}
            ref={textArea}
          >
          </textarea>
          <div className={styles.attachButton}>
          </div>
          <div className={styles.sendButton} onClick={handleSendMessage}>
            send
          </div>
        </div>
      </>
    );
};
export default CreateMessage;
