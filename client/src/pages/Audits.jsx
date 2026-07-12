import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';

export default function Audits() {
  const [cycles, setCycles] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ name: '', departmentId: '', location: '', startDate: '', endDate: '' });

  useEffect(() => {
    fetchCycles();
  }, []);

  const fetchCycles = async () => {
    try {
      const res = await axios.get('/api/audits');
      setCycles(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/audits', form);
      setShowDialog(false);
      fetchCycles();
    } catch (err) {
      console.error(err);
    }
  };

  const handleClose = async (id) => {
    if (window.confirm('Close this audit cycle?')) {
      await axios.post(`/api/audits/${id}/close`);
      fetchCycles();
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Audit Cycles</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild><Button>Create Audit Cycle</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Create Audit Cycle</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              <Input placeholder="Department ID (optional)" value={form.departmentId} onChange={e => setForm({...form, departmentId: e.target.value})} />
              <Input placeholder="Location (optional)" value={form.location} onChange={e => setForm({...form, location: e.target.value})} />
              <Input type="date" placeholder="Start Date" value={form.startDate} onChange={e => setForm({...form, startDate: e.target.value})} required />
              <Input type="date" placeholder="End Date" value={form.endDate} onChange={e => setForm({...form, endDate: e.target.value})} required />
              <Button type="submit">Create</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Department</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Period</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {cycles.map(c => (
            <TableRow key={c.id}>
              <TableCell>{c.name}</TableCell>
              <TableCell>{c.department?.name || 'All'}</TableCell>
              <TableCell>{c.location || 'N/A'}</TableCell>
              <TableCell>{new Date(c.startDate).toLocaleDateString()} - {new Date(c.endDate).toLocaleDateString()}</TableCell>
              <TableCell>{c.status}</TableCell>
              <TableCell>
                {c.status === 'Open' && <Button size="sm" onClick={() => handleClose(c.id)}>Close</Button>}
                {c.discrepancyReport && <Button size="sm" variant="outline" onClick={() => alert(c.discrepancyReport)}>View Report</Button>}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}