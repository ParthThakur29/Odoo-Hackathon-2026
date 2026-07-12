import React, { useState, useEffect } from 'react';
import axios from '../api/client';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Select, SelectTrigger, SelectContent, SelectItem } from '../components/ui/select';

export default function Organization() {
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [deptForm, setDeptForm] = useState({ name: '', parentId: '', headId: '' });
  const [catForm, setCatForm] = useState({ name: '', description: '', extraFields: '' });
  const [empForm, setEmpForm] = useState({});
  const [showDeptDialog, setShowDeptDialog] = useState(false);
  const [showCatDialog, setShowCatDialog] = useState(false);

  useEffect(() => {
    fetchDepartments();
    fetchCategories();
    fetchEmployees();
  }, []);

  const fetchDepartments = async () => {
    const res = await axios.get('/api/departments');
    setDepartments(res.data);
  };
  const fetchCategories = async () => {
    const res = await axios.get('/api/categories');
    setCategories(res.data);
  };
  const fetchEmployees = async () => {
    const res = await axios.get('/api/employees');
    setEmployees(res.data);
  };

  const handleDeptSubmit = async (e) => {
    e.preventDefault();
    await axios.post('/api/departments', deptForm);
    setShowDeptDialog(false);
    fetchDepartments();
  };
  const handleCatSubmit = async (e) => {
    e.preventDefault();
    await axios.post('/api/categories', catForm);
    setShowCatDialog(false);
    fetchCategories();
  };
  const handleRoleChange = async (id, role) => {
    if (window.confirm(`Change role to ${role}?`)) {
      await axios.put(`/api/employees/${id}`, { role });
      fetchEmployees();
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Organization Setup</h2>
      <Tabs defaultValue="departments">
        <TabsList>
          <TabsTrigger value="departments">Departments</TabsTrigger>
          <TabsTrigger value="categories">Asset Categories</TabsTrigger>
          <TabsTrigger value="employees">Employees</TabsTrigger>
        </TabsList>

        <TabsContent value="departments">
          <div className="mb-4">
            <Dialog open={showDeptDialog} onOpenChange={setShowDeptDialog}>
              <DialogTrigger asChild><Button>Add Department</Button></DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Create Department</DialogTitle></DialogHeader>
                <form onSubmit={handleDeptSubmit} className="space-y-4">
                  <Input placeholder="Name" value={deptForm.name} onChange={e => setDeptForm({...deptForm, name: e.target.value})} required />
                  <Input placeholder="Parent Department ID (optional)" value={deptForm.parentId} onChange={e => setDeptForm({...deptForm, parentId: e.target.value})} />
                  <Input placeholder="Head Employee ID (optional)" value={deptForm.headId} onChange={e => setDeptForm({...deptForm, headId: e.target.value})} />
                  <Button type="submit">Create</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
          <Table>
            <TableHeader>
              <TableRow><TableHead>Name</TableHead><TableHead>Head</TableHead><TableHead>Parent</TableHead><TableHead>Status</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {departments.map(d => (
                <TableRow key={d.id}>
                  <TableCell>{d.name}</TableCell>
                  <TableCell>{d.head?.name || 'None'}</TableCell>
                  <TableCell>{d.parent?.name || 'None'}</TableCell>
                  <TableCell>{d.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>

        <TabsContent value="categories">
          <div className="mb-4">
            <Dialog open={showCatDialog} onOpenChange={setShowCatDialog}>
              <DialogTrigger asChild><Button>Add Category</Button></DialogTrigger>
              <DialogContent>
                <DialogHeader><DialogTitle>Create Asset Category</DialogTitle></DialogHeader>
                <form onSubmit={handleCatSubmit} className="space-y-4">
                  <Input placeholder="Name" value={catForm.name} onChange={e => setCatForm({...catForm, name: e.target.value})} required />
                  <Input placeholder="Description" value={catForm.description} onChange={e => setCatForm({...catForm, description: e.target.value})} />
                  <Input placeholder="Extra fields (JSON)" value={catForm.extraFields} onChange={e => setCatForm({...catForm, extraFields: e.target.value})} />
                  <Button type="submit">Create</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
          <Table>
            <TableHeader>
              <TableRow><TableHead>Name</TableHead><TableHead>Description</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {categories.map(c => (
                <TableRow key={c.id}><TableCell>{c.name}</TableCell><TableCell>{c.description}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>

        <TabsContent value="employees">
          <Table>
            <TableHeader>
              <TableRow><TableHead>Name</TableHead><TableHead>Email</TableHead><TableHead>Department</TableHead><TableHead>Role</TableHead><TableHead>Actions</TableHead></TableRow>
            </TableHeader>
            <TableBody>
              {employees.map(e => (
                <TableRow key={e.id}>
                  <TableCell>{e.name}</TableCell>
                  <TableCell>{e.email}</TableCell>
                  <TableCell>{e.department?.name || 'None'}</TableCell>
                  <TableCell>{e.role}</TableCell>
                  <TableCell>
                    <Select onValueChange={val => handleRoleChange(e.id, val)}>
                      <SelectTrigger>Change Role</SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Employee">Employee</SelectItem>
                        <SelectItem value="DepartmentHead">Department Head</SelectItem>
                        <SelectItem value="AssetManager">Asset Manager</SelectItem>
                        <SelectItem value="Admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>
      </Tabs>
    </div>
  );
}