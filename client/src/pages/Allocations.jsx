import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Select, SelectTrigger, SelectContent, SelectItem } from '../components/ui/select';

export default function Allocations() {
  const [allocations, setAllocations] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ assetId: '', employeeId: '', departmentId: '', expectedReturnDate: '' });

  useEffect(() => {
    fetchAllocations();
  }, []);

  const fetchAllocations = async () => {
    try {
      const res = await axios.get('/api/allocations');
      setAllocations(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/allocations', form);
      setShowDialog(false);
      fetchAllocations();
    } catch (err) {
      alert(err.response?.data?.error || 'Error');
    }
  };

  const handleReturn = async (id) => {
    if (window.confirm('Mark this asset as returned?')) {
      await axios.post(`/api/allocations/${id}/return`, { conditionCheck: prompt('Condition check notes:') });
      fetchAllocations();
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Allocations</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>Allocate Asset</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Allocate Asset</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Asset ID" value={form.assetId} onChange={e => setForm({...form, assetId: e.target.value})} required />
              <Input placeholder="Employee ID" value={form.employeeId} onChange={e => setForm({...form, employeeId: e.target.value})} required />
              <Input placeholder="Department ID (optional)" value={form.departmentId} onChange={e => setForm({...form, departmentId: e.target.value})} />
              <Input type="date" placeholder="Expected Return Date" value={form.expectedReturnDate} onChange={e => setForm({...form, expectedReturnDate: e.target.value})} />
              <Button type="submit">Allocate</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Asset</TableHead>
            <TableHead>Employee</TableHead>
            <TableHead>Department</TableHead>
            <TableHead>Expected Return</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {allocations.map(a => (
            <TableRow key={a.id}>
              <TableCell>{a.asset?.tag} - {a.asset?.name}</TableCell>
              <TableCell>{a.employee?.name}</TableCell>
              <TableCell>{a.department?.name || 'N/A'}</TableCell>
              <TableCell>{a.expectedReturnDate ? new Date(a.expectedReturnDate).toLocaleDateString() : 'None'}</TableCell>
              <TableCell>{a.status}</TableCell>
              <TableCell>
                {a.status === 'Active' && <Button size="sm" onClick={() => handleReturn(a.id)}>Return</Button>}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}