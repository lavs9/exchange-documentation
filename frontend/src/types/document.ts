/**
 * Type definitions for documents and sections.
 */

export interface Document {
  id: string;
  title: string;
  version: string;
  upload_date: string;
  file_path: string;
  page_count: number | null;
  processing_status: DocumentStatus;
  metadata_: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export type DocumentStatus = 'processing' | 'completed' | 'failed';

export interface DocumentCreate {
  title: string;
  version: string;
  pdf_file: File;
  docling_json?: File;
  docling_md?: File;
}

export interface DocumentList {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
}

export interface Section {
  id: string;
  document_id: string;
  level: number;
  title: string;
  content: string;
  page_number: number | null;
  parent_id: string | null;
  order_index: number;
  file_path?: string;  // Path to chapter file for wikilinks and backlinks
  created_at: string;
  updated_at: string;
}

export interface TOCEntry {
  id: string;
  title: string;
  level: number;
  page_number: number | null;
  children: TOCEntry[];
}

export interface TableOfContents {
  document_id: string;
  entries: TOCEntry[];
}

export interface ProcessingStatus {
  document_id: string;
  status: DocumentStatus;
  progress: number | null;
}
