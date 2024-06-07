/*
 * formScope: all
 * formPath: /
 * formInfo: Корневая страница
 */
import React, { Suspense } from 'react';
import { Navigate, type RouteObject, useRoutes } from 'react-router-dom';

import './App.css'

const Login = React.lazy(async () => await import('./pages/Login/Login.tsx'));
const Registration = React.lazy(async () => await import('./pages/Registration/Registration.tsx'));

const createRoutes = (): RouteObject[] => [
  {
    path: '/',
    element: <Navigate to="/login" />,
    children: [
    ],
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/registration',
    element: <Registration />,
  },
  {
    path: '*',
    element: <Navigate to="/" />,
  },
];

const App: React.FC = () => {
  const customRouter = useRoutes(createRoutes());

  return (
    <Suspense>{customRouter}</Suspense>
  );
};

export default App;
