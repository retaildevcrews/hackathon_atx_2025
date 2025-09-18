import React from 'react';
import { EvaluationResult, EvaluationIndividualResult, EvaluationCriteriaScore } from '../../types/evaluations';
import { Box, Typography, Divider, Stack, Table, TableBody, TableCell, TableHead, TableRow, Paper, Collapse, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface Props {
  evaluation: EvaluationResult;
  candidateId: string;
}

// Attempts to extract candidate-specific info from evaluation
function findCandidateScore(evaluation: EvaluationResult, candidateId: string) {
  const cand = evaluation.candidates.find(c => c.candidate_id === candidateId);
  return cand;
}

export const CandidateEvaluationDetail: React.FC<Props> = ({ evaluation, candidateId }) => {
  const candidateEntry = findCandidateScore(evaluation, candidateId);

  // Attempt to locate the individual result object for this candidate
  const individual: EvaluationIndividualResult | undefined = evaluation.individual_results.find((r: any) =>
    r && typeof r === 'object' && r.candidate_id === candidateId
  );

  // Highest priority: criteria_evaluations (new structure example provided)
  const criteriaEvaluations: any[] = Array.isArray((individual as any)?.criteria_evaluations)
    ? (individual as any).criteria_evaluations
    : [];

  const criteria: EvaluationCriteriaScore[] = criteriaEvaluations.length === 0 && Array.isArray(individual?.criteria)
    ? (individual!.criteria as EvaluationCriteriaScore[])
    : criteriaEvaluations;

  // Look for alternative arrays like criteria_results
  let altCriteria: any[] = [];
  if (!criteria.length && individual && Array.isArray((individual as any).criteria_results)) {
    altCriteria = (individual as any).criteria_results;
  }

  const criteriaPool = criteria.length ? criteria : altCriteria;

  // Provide a best-effort alternative extraction: flatten keys that look like criteria
  const derivedCriteria: EvaluationCriteriaScore[] = criteria.length === 0 && individual
    ? Object.keys(individual)
        .filter(k => k.startsWith('criteria_') && typeof (individual as any)[k] === 'object')
        .map(k => ({ criteria_name: k.replace(/^criteria_/, ''), ...(individual as any)[k] }))
    : [];

  const hasVerboseKeys = criteriaPool.some(c => c && (c.criterion_name || c.criterion_description || c.reasoning));
  const verboseCriteria = hasVerboseKeys ? criteriaPool.map(c => ({
    criterion_name: c.criterion_name || c.criteria_name || c.criteria_id || c.name,
    criterion_description: c.criterion_description || c.description,
    weight: c.weight,
    score: c.score ?? c.overall_score,
    reasoning: c.reasoning || c.explanation || c.explanation_text,
  })) : [];

  const displayCriteria = verboseCriteria.length ? verboseCriteria : (criteria.length ? criteria : derivedCriteria);

  const hasCriteria = displayCriteria.length > 0;

  const [rawOpen, setRawOpen] = React.useState(false);

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 1 }}>Evaluation Details</Typography>
      <Divider sx={{ mb: 2 }} />
      <Stack spacing={1} sx={{ mb: 2 }}>
        <Typography variant="body2">Rubric: {evaluation.rubric_name}</Typography>
        <Typography variant="body2">Overall Score: {evaluation.overall_score.toFixed(2)}</Typography>
        <Typography variant="body2">Evaluated At: {new Date(evaluation.created_at).toLocaleString()}</Typography>
        {candidateEntry && (
            <Typography variant="body2">Candidate Score: {candidateEntry.candidate_score.toFixed(2)}{candidateEntry.rank != null && ` (Rank: ${candidateEntry.rank})`}</Typography>
        )}
      </Stack>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Criteria Breakdown</Typography>
      {!hasCriteria && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          No structured criteria data found for this evaluation result.
        </Typography>
      )}
      {hasCriteria && (
        <Paper variant="outlined" sx={{ mb: 2, overflowX: 'auto' }}>
          <Table size="small" aria-label="criteria scores">
            <TableHead>
              <TableRow>
                <TableCell>Criterion</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="right">Weight</TableCell>
                <TableCell align="right">Score</TableCell>
                <TableCell>Reasoning</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayCriteria.map((c: any, idx: number) => {
                const criterionName = c.criterion_name || c.criteria_name || c.criteria_id || c.name || `#${idx+1}`;
                const desc = c.criterion_description || c.description || '';
                const weight = c.weight != null ? Number(c.weight) : null;
                const score = c.score != null ? Number(c.score) : null;
                const reasoning = c.reasoning || c.explanation || '';
                return (
                  <TableRow key={idx}>
                    <TableCell>{criterionName}</TableCell>
                    <TableCell style={{ maxWidth: 260 }}>
                      <Typography variant="caption" sx={{ display: 'block' }}>{desc}</Typography>
                    </TableCell>
                    <TableCell align="right">{weight != null ? weight.toFixed(2) : '-'}</TableCell>
                    <TableCell align="right">{score != null ? score.toFixed(2) : '-'}</TableCell>
                    <TableCell style={{ maxWidth: 320 }}>
                      <Typography variant="caption" sx={{ display: 'block' }}>{reasoning}</Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Paper>
      )}
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <Typography variant="subtitle2">Raw Individual Result</Typography>
        <IconButton size="small" onClick={() => setRawOpen(o => !o)} aria-label={rawOpen ? 'collapse raw json' : 'expand raw json'}>
          {rawOpen ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
        </IconButton>
      </Stack>
      <Collapse in={rawOpen} unmountOnExit>
        <Paper variant="outlined" sx={{ p: 1, maxHeight: 240, overflow: 'auto', fontSize: '0.75rem', backgroundColor: 'background.default' }}>
          <pre style={{ margin: 0 }}>{JSON.stringify(individual || {}, null, 2)}</pre>
        </Paper>
      </Collapse>
    </Box>
  );
};
