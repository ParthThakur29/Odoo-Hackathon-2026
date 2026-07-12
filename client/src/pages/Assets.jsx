import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Select, SelectTrigger, SelectContent, SelectItem } from '../components/ui/select';

export default function Assets() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ name: '', categoryId: '', serialNumber: '', acquisitionDate: '', acquisitionCost: '', condition: 'Good', location: '', isShared: false, departmentId: '' });

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const res = await axios.get('/api/assets');
      setAssets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/assets', form);
      setShowDialog(false);
      fetchAssets();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Assets</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>Register Asset</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Register Asset</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input placeholder="Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              <Input placeholder="Category ID" value={form.categoryId} onChange={e => setForm({...form, categoryId: e.target.value})} required />
              <Input placeholder="Serial Number" value={form.serialNumber} onChange={e => setForm({...form, serialNumber: e.target.value})} />
              <Input type="date" placeholder="Acquisition Date" value={form.acquisitionDate} onChange={e => setForm({...form, acquisitionDate: e.target.value})} />
              <Input placeholder="Acquisition Cost" value={form.acquisitionCost} onChange={e => setForm({...form, acquisitionCost: e.target.value})} />
              <Input placeholder="Location" value={form.location} onChange={e => setForm({...form, location: e.target.value})} />
              <Select value={form.condition} onValueChange={val => setForm({...form, condition: val})}>
                <SelectTrigger>Condition</SelectTrigger>
                <SelectContent>
                  <SelectItem value="Good">Good</SelectItem>
                  <SelectItem value="Fair">Fair</SelectItem>
                  <SelectItem value="Poor">Poor</SelectItem>
                </SelectContent>
              </Select>
              <Button type="submit">Create</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Tag</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Location</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {assets.map(asset => (
            <TableRow key={asset.id}>
              <TableCell>{asset.tag}</TableCell>
              <TableCell>{asset.name}</TableCell>
              <TableCell>{asset.category?.name}</TableCell>
              <TableCell>{asset.status}</TableCell>
              <TableCell>{asset.location}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}