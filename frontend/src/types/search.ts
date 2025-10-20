/**
 * Type definitions for search functionality.
 */

export interface SearchResult {
  section_id: string;
  document_id: string;
  title: string;
  snippet: string;
  page_number: number | null;
  rank: number;
  level: number;
}

export interface SearchResults {
  results: SearchResult[];
  total: number;
  page: number;
  page_size: number;
  query: string;
}

export interface SearchQuery {
  query: string;
  filter_type?: SearchFilter;
  page?: number;
  page_size?: number;
}

export type SearchFilter = 'all' | 'chapter' | 'section';
