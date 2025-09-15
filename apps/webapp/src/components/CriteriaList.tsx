import React from 'react';
import { useCriteria } from '../hooks/useCriteria';

export const CriteriaList: React.FC = () => {
  const { criteria, loading, error, refresh, remove } = useCriteria();

  if (loading) return <p>Loading criteria...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Existing Criteria</h2>
      <button onClick={refresh}>Refresh</button>
      {criteria.length === 0 && <p>No criteria yet.</p>}
      <ul>
        {criteria.map(c => (
          <li key={c.id} style={{ marginBottom: '0.5rem' }}>
            <strong>{c.name}</strong> — {c.description}
            <button style={{ marginLeft: '0.5rem' }} onClick={() => remove(c.id!)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};
