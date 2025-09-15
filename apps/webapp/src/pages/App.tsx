import React from 'react';
import { CriteriaList } from '../components/CriteriaList';
import { CreateCriteriaForm } from '../components/CreateCriteriaForm';

export const App: React.FC = () => {
  return (
    <div style={{ fontFamily: 'system-ui', margin: '1rem 2rem' }}>
      <h1>Criteria Manager</h1>
      <CreateCriteriaForm />
      <hr />
      <CriteriaList />
    </div>
  );
};
