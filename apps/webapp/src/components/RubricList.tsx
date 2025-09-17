import React from 'react';
import { Rubric } from '../types/rubric';
import { List, ListItem, ListItemButton, ListItemText, Typography, Paper, Divider } from '@mui/material';

interface RubricListProps {
  rubrics: Rubric[];
  onSelect: (rubric: Rubric) => void;
}

export const RubricList: React.FC<RubricListProps> = ({ rubrics, onSelect }) => {
  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Rubrics</Typography>
      <List>
        {rubrics.map((rubric, idx) => (
          <React.Fragment key={rubric.id}>
            <ListItem disablePadding>
              <ListItemButton onClick={() => onSelect(rubric)}>
                <ListItemText
                  primary={rubric.name}
                  secondary={rubric.description}
                />
              </ListItemButton>
            </ListItem>
            {idx < rubrics.length - 1 && <Divider component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};
