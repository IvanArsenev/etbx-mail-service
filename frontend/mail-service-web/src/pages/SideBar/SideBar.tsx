import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';

import styles from './SideBar.module.scss';

const SideBar: React.FC = () => {
    const [ isAuth, setIsAuth ] = useState<boolean>(false);

    if (isAuth) {
        return <Navigate to="/" />;
    }

    // const onFinish = ({ username, password }: UserAuth): void => {
    //     if (!isAuth) {
    //     }
    // };

    return (
        <>
          <div className={styles.SideBar}>
          
          </div>
        </>
    );
};
export default SideBar;
