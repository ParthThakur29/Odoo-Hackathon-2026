import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectTrigger, SelectContent, SelectItem } from '../components/ui/select';

export default function Maintenance() {
  const [requests, setRequests] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ assetId: '', description: '', priority: 'Medium', photo: '' });

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const res = await axios.get('/api/maintenance');
      setRequests(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/maintenance', form);
      setShowDialog(false);
      fetchRequests();
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (id) => {
    await axios.post(`/api/maintenance/${id}/approve`);
    fetchRequests();
  };

  const handleResolve = async (id) => {
    const note = prompt('Resolution note:');
    if (note !== null) {
      await axios.post(`/api/maintenance/${id}/resolve`, { resolutionNote: note });
      fetchRequests();
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Maintenance Requests</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild><Button>Raise Request</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Raise Maintenance Request</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Asset ID" value={form.assetId} onChange={e => setForm({...form, assetId: e.target.value})} required />
              <Textarea placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} required />
              <Select value={form.priority} onValueChange={val => setForm({...form, priority: val})}>
                <SelectTrigger>Priority</SelectTrigger>
                <SelectContent>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder="Photo URL (optional)" value={form.photo} onChange={e => setForm({...form, photo: e.target.value})} />
              <Button type="submit">Submit</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Asset</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {requests.map(r => (
            <TableRow key={r.id}>
              <TableCell>{r.asset?.name}</TableCell>
              <TableCell>{r.description}</TableCell>
              <TableCell>{r.priority}</TableCell>
              <TableCell>{r.status}</TableCell>
              <TableCell>
                {r.status === 'Pending' && <Button size="sm" onClick={() => handleApprove(r.id)}>Approve</Button>}
                {r.status === 'Approved' && <Button size="sm" onClick={() => handleResolve(r.id)}>Resolve</Button>}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}