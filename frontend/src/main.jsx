import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';
import NewPodcast from './NewPodcast';
import './style.css';

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  
  return token ? children : <Navigate to="/" />;
};

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route 
          path="/" element={<Login />} 
        />
        
        <Route 
          path="/dashboard" 
          element={ <PrivateRoute><Dashboard /></PrivateRoute> } 
        />

        <Route 
          path="/novo-podcast" 
          element={ <PrivateRoute><NewPodcast /></PrivateRoute> } 
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);