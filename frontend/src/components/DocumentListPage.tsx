import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Loader2, AlertCircle, Trash2, Eye } from 'lucide-react';
import { apiClient } from '../services/api';
import type { Document, DocumentCreate } from '../types';

const DocumentListPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [fileType, setFileType] = useState<'json' | 'markdown' | 'pdf'>('json');
  const navigate = useNavigate();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    const title = formData.get('title') as string;
    const version = formData.get('version') as string;

    if (!title || !version) {
      alert('Please fill all required fields');
      return;
    }

    // Build upload data based on file type
    const uploadFormData = new FormData();
    uploadFormData.append('title', title);
    uploadFormData.append('version', version);
    uploadFormData.append('file_type', fileType);

    if (fileType === 'json') {
      const jsonFile = formData.get('json_file') as File;
      if (!jsonFile) {
        alert('Please select a JSON file');
        return;
      }
      uploadFormData.append('file', jsonFile);
    } else if (fileType === 'markdown') {
      const mdFile = formData.get('md_file') as File;
      if (!mdFile) {
        alert('Please select a Markdown file');
        return;
      }
      uploadFormData.append('file', mdFile);
    } else if (fileType === 'pdf') {
      const pdfFile = formData.get('pdf_file') as File;
      const doclingMd = formData.get('docling_md') as File;
      const doclingJson = formData.get('docling_json') as File;

      if (!pdfFile) {
        alert('Please select a PDF file');
        return;
      }
      if (!doclingMd && !doclingJson) {
        alert('Please select either Docling JSON or Markdown file');
        return;
      }

      uploadFormData.append('file', pdfFile);
      if (doclingJson) {
        uploadFormData.append('docling_json', doclingJson);
      }
      if (doclingMd) {
        uploadFormData.append('docling_md', doclingMd);
      }
    }

    try {
      setUploading(true);
      await apiClient.uploadDocument(uploadFormData);
      alert('Document uploaded successfully!');
      loadDocuments();
      event.currentTarget.reset();
    } catch (err) {
      alert('Failed to upload document');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await apiClient.deleteDocument(documentId);
      loadDocuments();
    } catch (err) {
      alert('Failed to delete document');
      console.error(err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Upload className="h-5 w-5 mr-2" />
          Upload Document
        </h2>

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Document Title *
              </label>
              <input
                type="text"
                name="title"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="NSE NNF Protocol"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Version *
              </label>
              <input
                type="text"
                name="version"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="v6.1"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                File Type *
              </label>
              <select
                value={fileType}
                onChange={(e) => setFileType(e.target.value as 'json' | 'markdown' | 'pdf')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="json">JSON (Recommended - Chapter-based)</option>
                <option value="markdown">Markdown</option>
                <option value="pdf">PDF (Legacy)</option>
              </select>
            </div>
          </div>

          {/* File inputs based on selected type */}
          {fileType === 'json' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Docling JSON File * (.json)
              </label>
              <input
                type="file"
                name="json_file"
                accept=".json"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                📦 Chapter-based architecture: ~12 sections instead of 325. Includes rich formatting, callouts, and cross-references.
              </p>
            </div>
          )}

          {fileType === 'markdown' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Docling Markdown File * (.md)
              </label>
              <input
                type="file"
                name="md_file"
                accept=".md,.markdown"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Standard section-based parsing from Docling markdown output.
              </p>
            </div>
          )}

          {fileType === 'pdf' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  PDF File *
                </label>
                <input
                  type="file"
                  name="pdf_file"
                  accept=".pdf"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Docling JSON (Optional)
                  </label>
                  <input
                    type="file"
                    name="docling_json"
                    accept=".json"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Docling Markdown (Optional)
                  </label>
                  <input
                    type="file"
                    name="docling_md"
                    accept=".md"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <p className="text-sm text-gray-500">
                * At least one Docling output file (JSON or Markdown) is required
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={uploading}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload Document
              </>
            )}
          </button>
        </form>
      </div>

      {/* Documents List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-500 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        <div className="divide-y divide-gray-200">
          {documents.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No documents uploaded yet</p>
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">
                          {doc.title}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {doc.version} • {doc.page_count || '?'} pages •{' '}
                          {new Date(doc.upload_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                        doc.processing_status
                      )}`}
                    >
                      {doc.processing_status}
                    </span>

                    {doc.processing_status === 'completed' && (
                      <button
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                        title="View document"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    )}

                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentListPage;
