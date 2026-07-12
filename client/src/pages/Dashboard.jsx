import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import axios from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { useNotifications } from '../hooks/useSocket';

export default function Dashboard() {
  const [stats, setStats] = useState({});
  const [overdue, setOverdue] = useState([]);
  const [recent, setRecent] = useState([]);
  const { user } = useAuth();
  const { notifications } = useNotifications();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, overdueRes, recentRes] = await Promise.all([
          axios.get('/api/assets/stats'),
          axios.get('/api/allocations/overdue'),
          axios.get('/api/activity/recent')
        ]);
        setStats(statsRes.data);
        setOverdue(overdueRes.data);
        setRecent(recentRes.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <div className="flex gap-2">
          <Button>Register Asset</Button>
          <Button>Book Resource</Button>
          <Button>Raise Request</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader><CardTitle>Available Assets</CardTitle></CardHeader>
          <CardContent><span className="text-3xl">{stats.available || 0}</span></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Allocated Assets</CardTitle></CardHeader>
          <CardContent><span className="text-3xl">{stats.allocated || 0}</span></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Active Bookings</CardTitle></CardHeader>
          <CardContent><span className="text-3xl">{stats.activeBookings || 0}</span></CardContent>
        </Card>
      </div>

      {overdue.length > 0 && (
        <Card className="border-red-300">
          <CardHeader><CardTitle className="text-red-600">Overdue Returns</CardTitle></CardHeader>
          <CardContent>
            <ul>
              {overdue.map(item => (
                <li key={item.id} className="text-sm py-1">Asset {item.asset.tag} overdue by {item.days} days</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div>
        <h3 className="text-lg font-semibold mb-2">Recent Activity</h3>
        <ul className="space-y-1 text-sm">
          {recent.map((act, idx) => (
            <li key={idx} className="text-gray-700">{act}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Notifications</h3>
        {notifications.map((n, idx) => (
          <div key={idx} className="bg-blue-50 p-2 rounded mb-1 text-sm">{n.message}</div>
        ))}
      </div>
    </div>
  );
}