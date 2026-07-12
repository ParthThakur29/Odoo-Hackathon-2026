import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';

export default function Bookings() {
  const [bookings, setBookings] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ assetId: '', startTime: '', endTime: '' });

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const res = await axios.get('/api/bookings');
      setBookings(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/bookings', form);
      setShowDialog(false);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.error || 'Booking failed');
    }
  };

  const handleCancel = async (id) => {
    if (window.confirm('Cancel this booking?')) {
      await axios.delete(`/api/bookings/${id}`);
      fetchBookings();
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Resource Bookings</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild><Button>Book Resource</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Book Resource</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Asset ID" value={form.assetId} onChange={e => setForm({...form, assetId: e.target.value})} required />
              <Input type="datetime-local" placeholder="Start Time" value={form.startTime} onChange={e => setForm({...form, startTime: e.target.value})} required />
              <Input type="datetime-local" placeholder="End Time" value={form.endTime} onChange={e => setForm({...form, endTime: e.target.value})} required />
              <Button type="submit">Book</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Resource</TableHead>
            <TableHead>Booked By</TableHead>
            <TableHead>Start</TableHead>
            <TableHead>End</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {bookings.map(b => (
            <TableRow key={b.id}>
              <TableCell>{b.asset?.name} ({b.asset?.tag})</TableCell>
              <TableCell>{b.employee?.name}</TableCell>
              <TableCell>{new Date(b.startTime).toLocaleString()}</TableCell>
              <TableCell>{new Date(b.endTime).toLocaleString()}</TableCell>
              <TableCell>{b.status}</TableCell>
              <TableCell>
                {b.status !== 'Cancelled' && <Button size="sm" variant="outline" onClick={() => handleCancel(b.id)}>Cancel</Button>}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}