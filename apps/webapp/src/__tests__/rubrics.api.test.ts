// Mock the API base resolution
jest.mock('../config/api', () => ({
  resolveApiBase: () => 'http://localhost:3000/api'
}));

// Mock axios
const mockGet = jest.fn();
const mockPost = jest.fn();
const mockPut = jest.fn();
const mockDelete = jest.fn();

jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: mockGet,
    post: mockPost,
    put: mockPut,
    delete: mockDelete,
  })),
}));

import {
  createRubric,
  updateRubric,
  deleteRubric,
  fetchAvailableCriteria,
  fetchRubricDetail
} from '../api/rubrics';

describe('Rubrics API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createRubric', () => {
    it('creates a rubric successfully', async () => {
      const newRubric = {
        name: 'Test Rubric',
        description: 'Test Description',
        criteria: []
      };

      const expectedResponse = {
        data: {
          id: '123',
          ...newRubric
        }
      };

      mockPost.mockResolvedValue(expectedResponse);

      const result = await createRubric(newRubric);

      expect(mockPost).toHaveBeenCalledWith('/rubrics/', {
        name: 'Test Rubric',
        description: 'Test Description',
        criteria: []
      });
      expect(result).toEqual(expectedResponse.data);
    });

    it('throws error when name is missing', async () => {
      const invalidRubric = {
        name: '',
        description: 'Test Description',
        criteria: []
      };

      await expect(createRubric(invalidRubric)).rejects.toThrow('Rubric name is required');
      expect(mockPost).not.toHaveBeenCalled();
    });

    it('trims whitespace from name and description', async () => {
      const rubricWithWhitespace = {
        name: '  Test Rubric  ',
        description: '  Test Description  ',
        criteria: []
      };

      const expectedResponse = {
        data: {
          id: '123',
          name: 'Test Rubric',
          description: 'Test Description',
          criteria: []
        }
      };

      mockPost.mockResolvedValue(expectedResponse);

      await createRubric(rubricWithWhitespace);

      expect(mockPost).toHaveBeenCalledWith('/rubrics/', {
        name: 'Test Rubric',
        description: 'Test Description',
        criteria: []
      });
    });
  });

  describe('updateRubric', () => {
    it('updates a rubric successfully', async () => {
      const updates = {
        name: 'Updated Rubric',
        description: 'Updated Description'
      };

      const expectedResponse = {
        data: {
          id: '123',
          ...updates,
          criteria: []
        }
      };

      mockPut.mockResolvedValue(expectedResponse);

      const result = await updateRubric('123', updates);

      expect(mockPut).toHaveBeenCalledWith('/rubrics/123', {
        name: 'Updated Rubric',
        description: 'Updated Description'
      });
      expect(result).toEqual(expectedResponse.data);
    });

    it('throws error when ID is missing', async () => {
      await expect(updateRubric('', { name: 'Test' })).rejects.toThrow('Rubric ID is required');
      expect(mockPut).not.toHaveBeenCalled();
    });
  });

  describe('deleteRubric', () => {
    it('deletes a rubric successfully', async () => {
      mockDelete.mockResolvedValue({});

      await deleteRubric('123');

      expect(mockDelete).toHaveBeenCalledWith('/rubrics/123');
    });

    it('throws error when ID is missing', async () => {
      await expect(deleteRubric('')).rejects.toThrow('Rubric ID is required');
      expect(mockDelete).not.toHaveBeenCalled();
    });
  });

  describe('fetchRubricDetail', () => {
    it('fetches rubric detail successfully', async () => {
      const rubricDetail = {
        id: '123',
        name: 'Test Rubric',
        description: 'Test Description',
        criteria: []
      };

      mockGet.mockResolvedValue({ data: rubricDetail });

      const result = await fetchRubricDetail('123');

      expect(mockGet).toHaveBeenCalledWith('/rubrics/123');
      expect(result).toEqual(rubricDetail);
    });

    it('throws error when ID is missing', async () => {
      await expect(fetchRubricDetail('')).rejects.toThrow('Missing rubric id');
      expect(mockGet).not.toHaveBeenCalled();
    });
  });

  describe('fetchAvailableCriteria', () => {
    it('fetches available criteria successfully', async () => {
      const criteria = [
        { id: '1', name: 'Criteria 1', description: 'First criteria' },
        { id: '2', name: 'Criteria 2', description: 'Second criteria' }
      ];

      mockGet.mockResolvedValue({ data: criteria });

      const result = await fetchAvailableCriteria();

      expect(mockGet).toHaveBeenCalledWith('/criteria/');
      expect(result).toEqual(criteria);
    });
  });
});
