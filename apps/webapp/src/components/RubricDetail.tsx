import React from 'react';
import { Rubric } from '../types/rubric';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Divider, Stack } from '@mui/material';

interface RubricDetailProps {
  rubric: Rubric;
}

export const RubricDetail: React.FC<RubricDetailProps> = ({ rubric }) => {
  const criteriaHeadingId = 'rubric-criteria-heading';
  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h5">{rubric.name}</Typography>
          <Typography variant="body1" color="text.secondary">{rubric.description}</Typography>
          <Typography id={criteriaHeadingId} variant="h6">Criteria</Typography>
        </Stack>
        <List aria-labelledby={criteriaHeadingId}>
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
