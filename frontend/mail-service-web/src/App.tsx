/*
 * formScope: all
 * formPath: /
 * formInfo: Корневая страница
 */
import React, { Suspense } from 'react';
import { Navigate, type RouteObject, useRoutes } from 'react-router-dom';

import './App.css'

const SideBar = React.lazy(async () => await import('./pages/SideBar/SideBar'));
const Chat = React.lazy(async () => await import('./pages/Chat/Chat'));
const Users = React.lazy(async () => await import('./pages/Users/Users'));
const Chats = React.lazy(async () => await import('./pages/Chats/Chats'));
const Registration = React.lazy(async () => await import('./pages/Registration/Registration'));
const Login = React.lazy(async () => await import('./pages/Login/Login'));

const createRoutes = (): RouteObject[] => [
  {
    path: '/',
    element: <Navigate to="/registration" />,
    children: [
    ],
  },
  {
    path: '/users',
    element: <>
      <SideBar />
      <Users />
    </>,
  },
  {
    path: '/users/:id',
    element: (
      <>
        <SideBar />
        <Chats />
      </>
    ),
  },
  {
    path: '/registration',
    element: <Registration />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '*',
    element: <Navigate to="/" />,
  },
];

const App: React.FC = () => {
  const customRouter = useRoutes(createRoutes());

  return (
    <div className={'container'}>
      <div style={{width: '100%', display: 'flex', height: '100vh'}}>
        <Suspense>
          {customRouter}
        </Suspense>
      </div>
    </div>
  );
};

export default App;
