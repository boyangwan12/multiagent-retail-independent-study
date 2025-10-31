/**
 * Category Type Definitions
 *
 * Types for product categories used in parameter gathering
 */

export interface Category {
  id: string;
  name: string;
  description?: string;
}

/**
 * API Response for category list
 */
export interface CategoryListResponse {
  categories: Category[];
}
