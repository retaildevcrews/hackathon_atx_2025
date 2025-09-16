import React, { useState } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Collapse, Box, Typography, Paper
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import type { RubricCriterionEntry } from '../types/decisionKits';

export interface EnrichedCriterion extends RubricCriterionEntry {
  description?: string;
  definition?: string;
}

interface Props {
  criteria: EnrichedCriterion[];
  loading?: boolean;
}

const Row: React.FC<{ c: EnrichedCriterion; }> = ({ c }) => {
  const [open, setOpen] = useState(false);
  const hasDefinition = !!c.definition;
  return (
    <>
      <TableRow hover role="row" aria-label={`criterion-${c.criteria_id}`}>
        <TableCell padding="checkbox">
          <IconButton size="small" aria-label={open ? 'collapse definition' : 'expand definition'} disabled={!hasDefinition} onClick={() => setOpen(o => !o)}>
            {hasDefinition ? (open ? <KeyboardArrowUpIcon fontSize="small" /> : <KeyboardArrowDownIcon fontSize="small" />) : <InfoOutlinedIcon fontSize="small" color="disabled" />}
          </IconButton>
        </TableCell>
        <TableCell sx={{ width: '30%' }}><Typography variant="body2" noWrap>{c.name || `Criteria ${c.criteria_id}`}</Typography></TableCell>
        <TableCell sx={{ width: '55%' }}>
          <Typography variant="body2" className="twoLineClamp">{c.description || '—'}</Typography>
        </TableCell>
        <TableCell sx={{ width: '15%' }} align="right">
          <Typography variant="body2" fontWeight={500}>{c.weight}</Typography>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ p: 2, bgcolor: 'background.default', borderLeft: '4px solid', borderColor: 'primary.light' }}>
              <Typography variant="subtitle2" gutterBottom>Definition</Typography>
              <Typography variant="body2" whiteSpace="pre-line">{c.definition}</Typography>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

export const RubricCriteriaTable: React.FC<Props> = ({ criteria, loading }) => {
  return (
    <TableContainer component={Paper} variant="outlined" sx={{ mt: 1 }}>
      <Table size="small" aria-label="rubric criteria table">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell align="right">Weight</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {criteria.map((c, i) => <Row key={c.criteria_id + '-' + i} c={c} />)}
          {(!criteria || criteria.length === 0) && !loading && (
            <TableRow>
              <TableCell colSpan={4}>
                <Typography variant="body2" color="text.secondary">No criteria.</Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
