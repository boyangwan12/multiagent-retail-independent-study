/**
 * Category Service
 *
 * Handles API calls related to product categories
 */

import { apiClient } from '@/utils/api-client';
import { API_ENDPOINTS } from '@/config/api';
import type { Category, CategoryListResponse } from '@/types/category';

export class CategoryService {
  /**
   * Fetch all available categories
   */
  static async getCategories(): Promise<Category[]> {
    const response = await apiClient.get<CategoryListResponse>(
      API_ENDPOINTS.categories.list()
    );

    return response.data.categories;
  }

  /**
   * Fetch a single category by ID
   */
  static async getCategoryById(id: string): Promise<Category> {
    const response = await apiClient.get<Category>(
      API_ENDPOINTS.categories.getById(id)
    );

    return response.data;
  }
}
