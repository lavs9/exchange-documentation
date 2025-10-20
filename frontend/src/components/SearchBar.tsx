/**
 * SearchBar Component
 *
 * Features:
 * - Real-time search with debounce (500ms)
 * - Display results with highlighted snippets
 * - Click to jump to result section
 * - Show search count and loading state
 * - Filter by section type
 */
import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2, FileText, ChevronDown } from 'lucide-react';
import clsx from 'clsx';
import { useDebounce } from '../hooks/useDebounce';
import { apiClient } from '../services/api';
import type { SearchResults, SearchResult, SearchFilter } from '../types';

interface SearchBarProps {
  documentId: string;
  onResultClick?: (sectionId: string) => void;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  documentId,
  onResultClick,
  className,
}) => {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<SearchFilter>('all');
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 500);
  const searchRef = useRef<HTMLDivElement>(null);

  // Search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.trim().length >= 2) {
      performSearch(debouncedQuery);
    } else {
      setResults(null);
      setIsOpen(false);
    }
  }, [debouncedQuery, filter, documentId]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.searchDocument(documentId, {
        query: searchQuery,
        filter_type: filter,
        page: 1,
        page_size: 10,
      });
      setResults(data);
      setIsOpen(true);
    } catch (err) {
      setError('Search failed');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    if (!e.target.value.trim()) {
      setResults(null);
      setIsOpen(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults(null);
    setIsOpen(false);
  };

  const handleResultClick = (result: SearchResult) => {
    onResultClick?.(result.section_id);
    setIsOpen(false);
  };

  const handleFilterChange = (newFilter: SearchFilter) => {
    setFilter(newFilter);
    if (query.trim().length >= 2) {
      performSearch(query);
    }
  };

  return (
    <div ref={searchRef} className={clsx('relative', className)}>
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>

        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Search document..."
          className="block w-full pl-10 pr-20 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />

        <div className="absolute inset-y-0 right-0 flex items-center pr-2 space-x-1">
          {loading && <Loader2 className="h-4 w-4 animate-spin text-gray-400" />}
          {query && !loading && (
            <button
              onClick={handleClear}
              className="p-1 hover:bg-gray-100 rounded"
              title="Clear search"
            >
              <X className="h-4 w-4 text-gray-400" />
            </button>
          )}

          {/* Filter Dropdown */}
          <div className="relative group">
            <button
              className="p-1 hover:bg-gray-100 rounded flex items-center"
              title="Filter results"
            >
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </button>

            <div className="absolute right-0 mt-1 w-40 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <div className="py-1">
                <button
                  onClick={() => handleFilterChange('all')}
                  className={clsx(
                    'w-full px-4 py-2 text-left text-sm hover:bg-gray-50',
                    filter === 'all' && 'bg-blue-50 text-blue-700'
                  )}
                >
                  All Sections
                </button>
                <button
                  onClick={() => handleFilterChange('chapter')}
                  className={clsx(
                    'w-full px-4 py-2 text-left text-sm hover:bg-gray-50',
                    filter === 'chapter' && 'bg-blue-50 text-blue-700'
                  )}
                >
                  Chapters Only
                </button>
                <button
                  onClick={() => handleFilterChange('section')}
                  className={clsx(
                    'w-full px-4 py-2 text-left text-sm hover:bg-gray-50',
                    filter === 'section' && 'bg-blue-50 text-blue-700'
                  )}
                >
                  Sections Only
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search Results Dropdown */}
      {isOpen && results && (
        <div className="absolute top-full mt-2 w-full bg-white border border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto z-20">
          {/* Results Header */}
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-600">
              Found <span className="font-semibold text-gray-900">{results.total}</span>{' '}
              {results.total === 1 ? 'result' : 'results'}
              {filter !== 'all' && ` in ${filter}s`}
            </p>
          </div>

          {/* Results List */}
          {results.results.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No results found for "{query}"</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-100">
              {results.results.map((result, index) => (
                <SearchResultItem
                  key={`${result.section_id}-${index}`}
                  result={result}
                  query={query}
                  onClick={() => handleResultClick(result)}
                />
              ))}
            </ul>
          )}

          {/* Show More Link */}
          {results.total > results.results.length && (
            <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 text-center">
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                Show {results.total - results.results.length} more results
              </button>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="absolute top-full mt-2 w-full bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
};

interface SearchResultItemProps {
  result: SearchResult;
  query: string;
  onClick: () => void;
}

const SearchResultItem: React.FC<SearchResultItemProps> = ({
  result,
  query,
  onClick,
}) => {
  const highlightText = (text: string, highlight: string) => {
    if (!highlight.trim()) return text;

    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === highlight.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 font-medium">
              {part}
            </mark>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </span>
    );
  };

  return (
    <li>
      <button
        onClick={onClick}
        className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start justify-between mb-1">
          <h4 className="text-sm font-medium text-gray-900 line-clamp-1">
            {highlightText(result.title, query)}
          </h4>
          {result.page_number && (
            <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
              p.{result.page_number}
            </span>
          )}
        </div>
        <p className="text-sm text-gray-600 line-clamp-2">
          {highlightText(result.snippet, query)}
        </p>
        <div className="mt-1 flex items-center text-xs text-gray-400">
          <span>Relevance: {(result.rank * 100).toFixed(0)}%</span>
          <span className="mx-2">•</span>
          <span>Level {result.level}</span>
        </div>
      </button>
    </li>
  );
};

export default SearchBar;
