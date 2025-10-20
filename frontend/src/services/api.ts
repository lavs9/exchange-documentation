/**
 * API client for backend communication.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Document,
  DocumentList,
  DocumentCreate,
  TableOfContents,
  ProcessingStatus,
  SearchResults,
  SearchQuery,
  Section,
} from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error status
          console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
        } else {
          // Error in request setup
          console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Document Management

  /**
   * Upload a new document (JSON, Markdown, or PDF with Docling files).
   */
  async uploadDocument(formData: FormData): Promise<Document> {
    const response = await this.client.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  /**
   * Get list of all documents.
   */
  async getDocuments(page: number = 1, pageSize: number = 20): Promise<DocumentList> {
    const response = await this.client.get<DocumentList>('/documents', {
      params: { page, page_size: pageSize },
    });

    return response.data;
  }

  /**
   * Get a single document by ID.
   */
  async getDocument(documentId: string): Promise<Document> {
    const response = await this.client.get<Document>(`/documents/${documentId}`);
    return response.data;
  }

  /**
   * Delete a document.
   */
  async deleteDocument(documentId: string): Promise<void> {
    await this.client.delete(`/documents/${documentId}`);
  }

  /**
   * Get processing status of a document.
   */
  async getProcessingStatus(documentId: string): Promise<ProcessingStatus> {
    const response = await this.client.get<ProcessingStatus>(
      `/documents/${documentId}/status`
    );
    return response.data;
  }

  // Navigation

  /**
   * Get table of contents for a document.
   */
  async getTableOfContents(documentId: string): Promise<TableOfContents> {
    const response = await this.client.get<TableOfContents>(
      `/documents/${documentId}/toc`
    );
    return response.data;
  }

  /**
   * Get a specific section.
   */
  async getSection(documentId: string, sectionId: string): Promise<Section> {
    const response = await this.client.get<Section>(
      `/documents/${documentId}/sections/${sectionId}`
    );
    return response.data;
  }

  /**
   * Update section content.
   */
  async updateSectionContent(
    documentId: string,
    sectionId: string,
    content: string
  ): Promise<Section> {
    const response = await this.client.put<Section>(
      `/documents/${documentId}/sections/${sectionId}`,
      { content }
    );
    return response.data;
  }

  // Search

  /**
   * Search within a document.
   */
  async searchDocument(
    documentId: string,
    searchQuery: SearchQuery
  ): Promise<SearchResults> {
    const response = await this.client.get<SearchResults>(
      `/documents/${documentId}/search`,
      {
        params: {
          q: searchQuery.query,
          filter_type: searchQuery.filter_type || 'all',
          page: searchQuery.page || 1,
          page_size: searchQuery.page_size || 20,
        },
      }
    );

    return response.data;
  }
}

// Create singleton instance
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const apiClient = new ApiClient(API_URL);
