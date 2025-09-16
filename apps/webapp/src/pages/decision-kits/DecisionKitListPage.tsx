import React from 'react';
import { Grid, Card, CardActionArea, CardContent, Typography, Skeleton, Box, Alert, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useDecisionKits } from '../../hooks/useDecisionKits';

const skeletonArray = Array.from({ length: 6 });

export const DecisionKitListPage: React.FC = () => {
  const { kits, loading, error, retry } = useDecisionKits();
  const navigate = useNavigate();

  if (error) {
    return <Alert severity="error" action={<Button color="inherit" size="small" onClick={retry}>Retry</Button>}>{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Decision Kits</Typography>
      <Grid container spacing={2}>
        {loading && !kits && skeletonArray.map((_, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <Card aria-label="loading decision kit" role="presentation">
              <CardContent>
                <Skeleton variant="text" width="70%" />
                <Skeleton variant="text" width="90%" />
                <Skeleton variant="rectangular" height={40} sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
        {!loading && kits && kits.length === 0 && (
          <Grid item xs={12}>
            <Alert severity="info">No decision kits yet.</Alert>
          </Grid>
        )}
  {kits && kits.map((k: any) => (
          <Grid item xs={12} sm={6} md={4} key={k.id}>
            <Card aria-label={`decision kit ${k.name}`}>
              <CardActionArea onClick={() => navigate(`/decision-kits/${k.id}`)}>
                <CardContent>
                  <Typography variant="h6" noWrap>{k.name}</Typography>
                  {k.description && (
                    <Typography variant="body2" sx={{ mt: 1 }} className="twoLineClamp">{k.description}</Typography>
                  )}
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
