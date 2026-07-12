import React, { useContext } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { AuthContext } from '../context/AuthContext';

export default function Layout() {
  const { user, logout } = useContext(AuthContext);
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar user={user} logout={logout} />
      <div className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </div>
    </div>
  );
}