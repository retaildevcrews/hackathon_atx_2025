import { fetchDecisionKit } from '../api/decisionKits';

jest.mock('axios', () => ({
  create: () => ({ get: jest.fn() })
}));

describe('decisionKits API', () => {
  it('throws on invalid (NaN) id without calling axios', async () => {
    await expect(fetchDecisionKit(Number.NaN as any)).rejects.toThrow(/Invalid decision kit id/);
  });
});
