import React, { useState } from 'react';
import { Container, AppBar, Toolbar, Typography, Box, Grid, Button, Paper } from '@mui/material';
import { RubricList } from '../components/RubricList';
import { RubricDetail } from '../components/RubricDetail';
import { RubricForm } from '../components/RubricForm';
import { useRubric } from '../hooks/useRubric';
import { Rubric } from '../types/rubric';

export const App: React.FC = () => {
  const { rubrics, createRubric, updateRubric, deleteRubric, loading } = useRubric();
  const [selectedRubric, setSelectedRubric] = useState<Rubric | null>(null);
  const [showForm, setShowForm] = useState(false);

  function handleSelectRubric(rubric: Rubric) {
    setSelectedRubric(rubric);
    setShowForm(false);
  }

  function handleCreateRubric(data: Omit<Rubric, 'id'>) {
    createRubric(data);
    setShowForm(false);
  }

  function handleEditRubric(data: Omit<Rubric, 'id'>) {
    if (selectedRubric) {
      updateRubric(selectedRubric.id, data);
      setShowForm(false);
    }
  }

  function handleDeleteRubric() {
    if (selectedRubric) {
      deleteRubric(selectedRubric.id);
      setSelectedRubric(null);
    }
  }

  return (
    <>
      <AppBar position="static" color="primary" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Criteria & Rubric Manager</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4, mb: 6 }}>
        <Paper sx={{ p: 2 }}>
          {!selectedRubric ? (
            <>
              <Typography variant="h5" sx={{ mb: 2 }}>Rubrics</Typography>
              <RubricList rubrics={rubrics} onSelect={handleSelectRubric} />
              <Button variant="contained" sx={{ mt: 2 }} onClick={() => { setShowForm(true); setSelectedRubric(null); }}>
                Add Rubric
              </Button>
              {showForm && (
                <RubricForm
                  onSave={handleCreateRubric}
                  loading={loading}
                />
              )}
            </>
          ) : (
            <>
              <Button variant="text" sx={{ mb: 2 }} onClick={() => setSelectedRubric(null)}>
                &larr; Back to Rubrics
              </Button>
              <RubricDetail rubric={selectedRubric} />
              <Button variant="outlined" sx={{ mt: 2, mr: 2 }} onClick={() => setShowForm(true)}>
                Edit
              </Button>
              <Button variant="outlined" color="error" sx={{ mt: 2 }} onClick={handleDeleteRubric}>
                Delete
              </Button>
              {showForm && (
                <RubricForm
                  initialRubric={selectedRubric}
                  onSave={handleEditRubric}
                  loading={loading}
                />
              )}
            </>
          )}
        </Paper>
      </Container>
    </>
  );
};
