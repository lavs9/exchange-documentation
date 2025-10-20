/**
 * Enhanced Table of Contents Component
 *
 * Features:
 * - Recursive rendering up to 4 levels
 * - Expand/collapse functionality with state persistence
 * - Scroll to section on click
 * - Highlight active section based on scroll position
 * - Sticky positioning
 */
import React, { useState, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import clsx from 'clsx';
import type { TOCEntry } from '../types';

interface TableOfContentsProps {
  entries: TOCEntry[];
  onSectionClick?: (sectionId: string) => void;
  activeSectionId?: string | null;
  /** Maximum nesting depth to display (default: 4) */
  maxDepth?: number;
}

const TableOfContents: React.FC<TableOfContentsProps> = ({
  entries,
  onSectionClick,
  activeSectionId,
  maxDepth = 4,
}) => {
  // Track expanded state for all entries
  const [expandedIds, setExpandedIds] = useState<Set<string>>(() => {
    // Auto-expand first 2 levels by default
    const initialExpanded = new Set<string>();
    const addToExpanded = (items: TOCEntry[], depth: number = 0) => {
      if (depth >= 2) return;
      items.forEach((item) => {
        if (item.children && item.children.length > 0) {
          initialExpanded.add(item.id);
          addToExpanded(item.children, depth + 1);
        }
      });
    };
    addToExpanded(entries);
    return initialExpanded;
  });

  const toggleExpanded = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleSectionClick = useCallback(
    (sectionId: string, hasChildren: boolean) => {
      // Scroll to section
      const element = document.querySelector(`[data-section-id="${sectionId}"]`);
      if (element) {
        const yOffset = -80; // Offset for fixed header
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }

      // Toggle expansion if has children
      if (hasChildren) {
        toggleExpanded(sectionId);
      }

      // Notify parent
      onSectionClick?.(sectionId);
    },
    [onSectionClick, toggleExpanded]
  );

  // Auto-expand parent sections when active section changes
  useEffect(() => {
    if (activeSectionId) {
      const findAndExpandParents = (items: TOCEntry[], targetId: string): boolean => {
        for (const item of items) {
          if (item.id === targetId) {
            return true;
          }
          if (item.children && item.children.length > 0) {
            if (findAndExpandParents(item.children, targetId)) {
              setExpandedIds((prev) => new Set(prev).add(item.id));
              return true;
            }
          }
        }
        return false;
      };
      findAndExpandParents(entries, activeSectionId);
    }
  }, [activeSectionId, entries]);

  // Scroll active item into view in the TOC
  useEffect(() => {
    if (activeSectionId) {
      const activeButton = document.querySelector(`[data-toc-id="${activeSectionId}"]`);
      if (activeButton) {
        activeButton.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
        });
      }
    }
  }, [activeSectionId]);

  return (
    <nav className="overflow-y-auto max-h-[calc(100vh-12rem)] scroll-smooth">
      <ul className="space-y-1">
        {entries.map((entry) => (
          <TOCEntryComponent
            key={entry.id}
            entry={entry}
            depth={0}
            maxDepth={maxDepth}
            isExpanded={expandedIds.has(entry.id)}
            isActive={activeSectionId === entry.id}
            onToggle={toggleExpanded}
            onSectionClick={handleSectionClick}
          />
        ))}
      </ul>
    </nav>
  );
};

interface TOCEntryProps {
  entry: TOCEntry;
  depth: number;
  maxDepth: number;
  isExpanded: boolean;
  isActive: boolean;
  onToggle: (id: string) => void;
  onSectionClick: (sectionId: string, hasChildren: boolean) => void;
}

const TOCEntryComponent: React.FC<TOCEntryProps> = ({
  entry,
  depth,
  maxDepth,
  isExpanded,
  isActive,
  onToggle,
  onSectionClick,
}) => {
  const hasChildren = entry.children && entry.children.length > 0 && depth < maxDepth;
  const showChildren = hasChildren && isExpanded;

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    onSectionClick(entry.id, hasChildren);
  };

  return (
    <li>
      <button
        data-toc-id={entry.id}
        onClick={handleClick}
        className={clsx(
          'w-full text-left px-2 py-1.5 rounded-md text-sm transition-all duration-200 flex items-start group',
          {
            'bg-blue-100 text-blue-700 font-medium': isActive,
            'hover:bg-gray-100 text-gray-700': !isActive,
            'font-semibold': entry.level === 1 || entry.level === 2,
            'font-medium': entry.level === 3 && !isActive,
            'font-normal': entry.level > 3,
          }
        )}
        style={{ paddingLeft: `${depth * 0.75 + 0.5}rem` }}
        title={entry.title}
      >
        {/* Expand/collapse icon */}
        {hasChildren && (
          <span
            className={clsx(
              'flex-shrink-0 mr-1 transition-transform duration-200',
              isExpanded ? '' : '-rotate-90'
            )}
          >
            <ChevronDown className="h-4 w-4" />
          </span>
        )}

        {/* Title and page number */}
        <span className="flex-1 break-words min-w-0">
          <span className="line-clamp-2">{entry.title}</span>
          {entry.page_number !== null && (
            <span className="text-xs text-gray-400 ml-2 whitespace-nowrap">
              p.{entry.page_number}
            </span>
          )}
        </span>
      </button>

      {/* Children */}
      {showChildren && (
        <ul className="mt-1 space-y-1">
          {entry.children.map((child) => (
            <TOCEntryComponent
              key={child.id}
              entry={child}
              depth={depth + 1}
              maxDepth={maxDepth}
              isExpanded={isActive ? true : false} // Auto-expand children of active section
              isActive={false} // Active state handled by parent
              onToggle={onToggle}
              onSectionClick={onSectionClick}
            />
          ))}
        </ul>
      )}
    </li>
  );
};

export default TableOfContents;
