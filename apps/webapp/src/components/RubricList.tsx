import React from 'react';
import { Rubric } from '../types/rubric';
import { List, ListItem, ListItemButton, ListItemText, Typography } from '@mui/material';

interface RubricListProps {
  rubrics: Rubric[];
  onSelect: (rubric: Rubric) => void;
}

export const RubricList: React.FC<RubricListProps> = ({ rubrics, onSelect }) => {
  return (
    <>
      <Typography variant="h6" sx={{ mb: 2 }}>Rubrics</Typography>
      <List>
        {rubrics.map(rubric => (
          <ListItem key={rubric.id} disablePadding>
            <ListItemButton onClick={() => onSelect(rubric)}>
              <ListItemText
                primary={rubric.name}
                secondary={rubric.description}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );
};
