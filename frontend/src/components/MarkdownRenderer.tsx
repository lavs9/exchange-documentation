/**
 * MarkdownRenderer Component
 *
 * Lightweight markdown renderer for read-only mode with custom component rendering.
 * Supports:
 * - Internal markers (<!-- MANUAL:START --> blocks)
 * - Callout blocks (Obsidian-style > [!type])
 * - Wikilinks ([[target]])
 * - Syntax-highlighted code blocks
 * - Styled tables
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import { AlertCircle, Info, Lightbulb, FileText } from 'lucide-react';
import 'highlight.js/styles/github-dark.css';

interface MarkdownRendererProps {
  content: string;
  documentId: string;
  version: string;
  onWikilinkClick?: (target: string, anchor?: string) => void;
}

interface ManualMarker {
  id: string;
  author: string;
  timestamp: string;
  type: string;
  content: string;
  startIndex: number;
  endIndex: number;
}

/**
 * Extract manual markers from markdown content
 */
const extractManualMarkers = (content: string): ManualMarker[] => {
  const markers: ManualMarker[] = [];
  const regex = /<!--\s*MANUAL:START:([^:]+):([^:]+):([^:]+)\s*-->([\s\S]*?)<!--\s*MANUAL:END\s*-->/g;

  let match;
  while ((match = regex.exec(content)) !== null) {
    markers.push({
      id: `marker-${markers.length}`,
      author: match[1],
      timestamp: match[2],
      type: match[3],
      content: match[4].trim(),
      startIndex: match.index,
      endIndex: match.index + match[0].length
    });
  }

  return markers;
};

/**
 * Remove manual marker HTML comments from content for rendering
 */
const stripManualMarkerTags = (content: string): string => {
  return content
    .replace(/<!--\s*MANUAL:START:[^>]+-->\s*/g, '<div class="manual-marker">')
    .replace(/\s*<!--\s*MANUAL:END\s*-->/g, '</div>');
};

/**
 * Process wikilinks for rendering
 */
const processWikilinks = (content: string): string => {
  return content.replace(/\[\[([^\]]+)\]\]/g, (match, linkText) => {
    const parts = linkText.split('#');
    const target = parts[0];
    const anchor = parts[1];

    const displayText = target.replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
    const dataAttr = anchor ? `data-wikilink="${target}" data-anchor="${anchor}"` : `data-wikilink="${target}"`;

    return `<span class="wikilink" ${dataAttr}>${displayText}</span>`;
  });
};

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  documentId,
  version,
  onWikilinkClick
}) => {
  // Extract markers and process content
  const markers = extractManualMarkers(content);
  const processedContent = processWikilinks(stripManualMarkerTags(content));

  // Handle wikilink clicks
  React.useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.classList.contains('wikilink')) {
        e.preventDefault();
        const wikilinkTarget = target.getAttribute('data-wikilink');
        const anchor = target.getAttribute('data-anchor');

        if (wikilinkTarget && onWikilinkClick) {
          onWikilinkClick(wikilinkTarget, anchor || undefined);
        }
      }
    };

    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [onWikilinkClick]);

  return (
    <div className="markdown-renderer prose prose-slate max-w-none">
      <style>{`
        .manual-marker {
          background-color: rgb(239 246 255); /* bg-blue-50 */
          border-left: 4px solid rgb(147 197 253); /* border-blue-300 */
          padding: 1rem;
          margin: 1rem 0;
          border-radius: 0.375rem;
          position: relative;
        }

        .manual-marker::before {
          content: 'Internal Note';
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          font-size: 0.75rem;
          color: rgb(59 130 246); /* text-blue-600 */
          font-weight: 600;
        }

        .wikilink {
          color: rgb(124 58 237); /* purple-600 */
          text-decoration: underline;
          cursor: pointer;
          font-weight: 500;
        }

        .wikilink:hover {
          color: rgb(109 40 217); /* purple-700 */
        }
      `}</style>

      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          // Custom blockquote renderer for callouts
          blockquote: ({ children }) => {
            // Extract text content to check for callout syntax
            const extractText = (node: any): string => {
              if (typeof node === 'string') return node;
              if (Array.isArray(node)) return node.map(extractText).join('');
              if (node?.props?.children) return extractText(node.props.children);
              return '';
            };

            const text = extractText(children);
            const calloutMatch = text.match(/^\[!(\w+)\]\s*(.+?)$/m);

            if (calloutMatch) {
              const [, type] = calloutMatch;
              const lowerType = type.toLowerCase();

              // Define callout styles
              const calloutStyles: Record<string, {
                border: string;
                bg: string;
                icon: React.ReactNode;
                label: string;
              }> = {
                important: {
                  border: 'border-blue-500',
                  bg: 'bg-blue-50',
                  icon: <Lightbulb className="w-5 h-5 text-blue-600" />,
                  label: 'Important'
                },
                info: {
                  border: 'border-blue-500',
                  bg: 'bg-blue-50',
                  icon: <Info className="w-5 h-5 text-blue-600" />,
                  label: 'Info'
                },
                warning: {
                  border: 'border-orange-500',
                  bg: 'bg-orange-50',
                  icon: <AlertCircle className="w-5 h-5 text-orange-600" />,
                  label: 'Warning'
                },
                tip: {
                  border: 'border-green-500',
                  bg: 'bg-green-50',
                  icon: <Lightbulb className="w-5 h-5 text-green-600" />,
                  label: 'Tip'
                },
                note: {
                  border: 'border-gray-500',
                  bg: 'bg-gray-50',
                  icon: <FileText className="w-5 h-5 text-gray-600" />,
                  label: 'Note'
                },
                callout: {
                  border: 'border-blue-500',
                  bg: 'bg-blue-50',
                  icon: <Lightbulb className="w-5 h-5 text-blue-600" />,
                  label: 'Callout'
                }
              };

              const style = calloutStyles[lowerType] || calloutStyles.info;

              return (
                <div className={`border-l-4 ${style.border} ${style.bg} p-4 my-4 rounded-r-lg`}>
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {style.icon}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold mb-1">{style.label}</div>
                      <div className="callout-content">
                        {children}
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            // Default blockquote style
            return (
              <blockquote className="border-l-4 border-gray-300 pl-4 py-2 my-4 italic text-gray-700">
                {children}
              </blockquote>
            );
          },

          // Styled code blocks
          code: ({ node, inline, className, children, ...props }) => {
            if (inline) {
              return (
                <code className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              );
            }

            return (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            );
          },

          // Responsive tables
          table: ({ children }) => (
            <div className="overflow-x-auto my-6">
              <table className="min-w-full divide-y divide-gray-300 border border-gray-300">
                {children}
              </table>
            </div>
          ),

          thead: ({ children }) => (
            <thead className="bg-gray-50">{children}</thead>
          ),

          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider border-b border-gray-300">
              {children}
            </th>
          ),

          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-gray-700 border-b border-gray-200">
              {children}
            </td>
          ),

          // Enhanced headings
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold mt-8 mb-4 text-gray-900">
              {children}
            </h1>
          ),

          h2: ({ children }) => (
            <h2 className="text-2xl font-bold mt-6 mb-3 text-gray-900">
              {children}
            </h2>
          ),

          h3: ({ children }) => (
            <h3 className="text-xl font-semibold mt-5 mb-2 text-gray-900">
              {children}
            </h3>
          ),

          h4: ({ children }) => (
            <h4 className="text-lg font-semibold mt-4 mb-2 text-gray-900">
              {children}
            </h4>
          ),

          // Enhanced lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-2 my-4 ml-4">
              {children}
            </ul>
          ),

          ol: ({ children }) => (
            <ol className="list-decimal list-inside space-y-2 my-4 ml-4">
              {children}
            </ol>
          ),

          // Enhanced links
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-blue-600 hover:text-blue-800 underline"
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
            >
              {children}
            </a>
          ),

          // Enhanced paragraphs
          p: ({ children }) => (
            <p className="my-4 text-gray-700 leading-relaxed">
              {children}
            </p>
          ),
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
