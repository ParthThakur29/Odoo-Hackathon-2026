import React, { createContext, useState, useEffect, useContext } from 'react';
import { io } from 'socket.io-client';
import { AuthContext } from './AuthContext';

export const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const { user } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    if (user) {
      const newSocket = io(window.location.origin, { withCredentials: true });
      setSocket(newSocket);
      newSocket.emit('join', user.id);
      newSocket.on('notification', (data) => {
        setNotifications(prev => [data, ...prev]);
      });
      return () => newSocket.disconnect();
    }
  }, [user]);

  return (
    <NotificationContext.Provider value={{ notifications, socket }}>
      {children}
    </NotificationContext.Provider>
  );
};