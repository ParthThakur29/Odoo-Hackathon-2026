import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Building2, Package, ArrowLeftRight, CalendarClock, Wrench, ClipboardList, Bell, LogOut } from 'lucide-react';

export default function Sidebar({ user, logout }) {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/assets', label: 'Assets', icon: Package },
    { path: '/allocations', label: 'Allocations', icon: ArrowLeftRight },
    { path: '/bookings', label: 'Bookings', icon: CalendarClock },
    { path: '/maintenance', label: 'Maintenance', icon: Wrench },
    { path: '/audits', label: 'Audits', icon: ClipboardList },
  ];
  if (user?.role === 'Admin') {
    navItems.push({ path: '/organization', label: 'Organization', icon: Building2 });
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b">
        <h1 className="text-2xl font-bold text-blue-600">AssetFlow</h1>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md transition ${isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium">{user?.name}</p>
            <p className="text-xs text-gray-500">{user?.role}</p>
          </div>
        </div>
        <button onClick={logout} className="flex items-center gap-2 text-sm text-gray-600 hover:text-red-600 w-full">
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </div>
  );
}