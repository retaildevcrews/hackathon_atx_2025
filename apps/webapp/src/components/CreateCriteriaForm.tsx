import React, { useState } from 'react';
import { useCriteria } from '../hooks/useCriteria';

export const CreateCriteriaForm: React.FC = () => {
  const { create } = useCriteria();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [definition, setDefinition] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    await create({ name, description, definition });
    setName('');
    setDescription('');
    setDefinition('');
  };

  return (
    <form onSubmit={submit} style={{ marginBottom: '1rem' }}>
      <h2>Create Criteria</h2>
      <div>
        <label>Name<br />
          <input value={name} onChange={e => setName(e.target.value)} required />
        </label>
      </div>
      <div>
        <label>Description<br />
          <input value={description} onChange={e => setDescription(e.target.value)} required />
        </label>
      </div>
      <div>
        <label>Definition (JSON or markdown)<br />
          <textarea value={definition} onChange={e => setDefinition(e.target.value)} rows={4} required />
        </label>
      </div>
      <button type="submit">Create</button>
    </form>
  );
};
