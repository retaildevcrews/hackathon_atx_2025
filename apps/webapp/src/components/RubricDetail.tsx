import React from 'react';
import { Rubric } from '../types/rubric';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Divider } from '@mui/material';

interface RubricDetailProps {
  rubric: Rubric;
}

export const RubricDetail: React.FC<RubricDetailProps> = ({ rubric }) => {
  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>{rubric.name}</Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>{rubric.description}</Typography>
        <Typography variant="h6" sx={{ mt: 2 }}>Criteria</Typography>
        <List>
          {rubric.criteria.map((c, idx) => (
            <React.Fragment key={c.id}>
              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={c.name}
                  secondaryTypographyProps={{ component: 'div' }}
                  secondary={
                    <>
                      <Typography variant="body2" color="text.secondary">{c.description}</Typography>
                      {c.definition && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                          {c.definition}
                        </Typography>
                      )}
                    </>
                  }
                />
              </ListItem>
              {idx < rubric.criteria.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};
