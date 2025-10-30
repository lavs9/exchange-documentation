/**
 * TipTap Markdown Serializer/Parser
 *
 * Converts between TipTap JSON and custom markdown format.
 * Handles:
 * - Internal markers (<!-- MANUAL:START --> ... <!-- MANUAL:END -->)
 * - Callout blocks (> [!type])
 * - Wikilinks ([[target]])
 * - Standard markdown (headings, lists, tables, code blocks)
 */

import { JSONContent } from '@tiptap/core';

export interface ManualMarker {
  id: string;
  author: string;
  timestamp: string;
  type: string;
  content: string;
}

/**
 * Extract manual markers from markdown
 */
export const extractManualMarkers = (markdown: string): ManualMarker[] => {
  const markers: ManualMarker[] = [];
  const regex = /<!--\s*MANUAL:START:([^:]+):([^:]+):([^:]+)\s*-->([\s\S]*?)<!--\s*MANUAL:END\s*-->/g;

  let match;
  while ((match = regex.exec(markdown)) !== null) {
    markers.push({
      id: `marker-${markers.length}`,
      author: match[1],
      timestamp: match[2],
      type: match[3],
      content: match[4].trim()
    });
  }

  return markers;
};

/**
 * Parse markdown to TipTap JSON
 * This is a simplified parser - for production, consider using a library like remark
 */
export const parseMarkdown = (markdown: string): JSONContent => {
  console.log('[parseMarkdown] Input length:', markdown?.length);
  console.log('[parseMarkdown] Has tables?', markdown?.includes('|'));

  const lines = markdown.split('\n');
  const content: JSONContent[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip empty lines at start
    if (!line.trim() && content.length === 0) {
      i++;
      continue;
    }

    // Manual markers
    if (line.includes('<!-- MANUAL:START')) {
      const markerMatch = line.match(/<!--\s*MANUAL:START:([^:]+):([^:]+):([^:]+)\s*-->/);
      if (markerMatch) {
        const [, author, timestamp, type] = markerMatch;
        const markerContent: string[] = [];
        i++;

        while (i < lines.length && !lines[i].includes('<!-- MANUAL:END')) {
          markerContent.push(lines[i]);
          i++;
        }

        content.push({
          type: 'internalMarker',
          attrs: {
            author,
            timestamp,
            type,
            id: `marker-${Date.now()}`
          },
          content: parseMarkdown(markerContent.join('\n')).content
        });
        i++;
        continue;
      }
    }

    // Callout blocks (blockquotes with [!type])
    if (line.startsWith('> [!')) {
      const calloutMatch = line.match(/>\s*\[!(\w+)\]/);
      if (calloutMatch) {
        const calloutType = calloutMatch[1].toLowerCase();
        const calloutLines: string[] = [];
        i++;

        while (i < lines.length && lines[i].startsWith('>')) {
          calloutLines.push(lines[i].replace(/^>\s?/, ''));
          i++;
        }

        content.push({
          type: 'callout',
          attrs: {
            type: calloutType
          },
          content: parseMarkdown(calloutLines.join('\n')).content
        });
        continue;
      }
    }

    // Headings
    if (line.startsWith('#')) {
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2];

        content.push({
          type: 'heading',
          attrs: { level },
          content: parseInlineContent(text)
        });
        i++;
        continue;
      }
    }

    // Code blocks
    if (line.startsWith('```')) {
      const language = line.slice(3).trim() || null;
      const codeLines: string[] = [];
      i++;

      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }

      content.push({
        type: 'codeBlock',
        attrs: { language },
        content: [
          {
            type: 'text',
            text: codeLines.join('\n')
          }
        ]
      });
      i++;
      continue;
    }

    // Bullet lists
    if (line.match(/^[\s]*[-*+]\s+/)) {
      const listItems: JSONContent[] = [];

      while (i < lines.length && lines[i].match(/^[\s]*[-*+]\s+/)) {
        const itemText = lines[i].replace(/^[\s]*[-*+]\s+/, '');
        listItems.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineContent(itemText)
            }
          ]
        });
        i++;
      }

      content.push({
        type: 'bulletList',
        content: listItems
      });
      continue;
    }

    // Numbered lists
    if (line.match(/^[\s]*\d+\.\s+/)) {
      const listItems: JSONContent[] = [];

      while (i < lines.length && lines[i].match(/^[\s]*\d+\.\s+/)) {
        const itemText = lines[i].replace(/^[\s]*\d+\.\s+/, '');
        listItems.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineContent(itemText)
            }
          ]
        });
        i++;
      }

      content.push({
        type: 'orderedList',
        content: listItems
      });
      continue;
    }

    // Tables (GitHub Flavored Markdown)
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      console.log('[parseMarkdown] Found table at line', i);
      const tableLines: string[] = [];

      // Collect all table lines
      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      console.log('[parseMarkdown] Collected', tableLines.length, 'table lines');

      if (tableLines.length >= 2) {
        // Parse table into rows
        const rows: JSONContent[] = [];
        let isFirstRow = true;

        for (let rowIndex = 0; rowIndex < tableLines.length; rowIndex++) {
          const rowLine = tableLines[rowIndex];

          // Skip separator row (| --- | --- |)
          if (rowLine.match(/^\|[\s\-:|]+\|$/)) {
            continue;
          }

          // Parse cells
          const cellTexts = rowLine
            .split('|')
            .slice(1, -1) // Remove empty strings from leading/trailing |
            .map(cell => cell.trim());

          const cells: JSONContent[] = cellTexts.map(cellText => {
            const inlineContent = parseInlineContent(cellText);
            // If cell is empty, add a space to prevent empty paragraph
            const content = inlineContent.length > 0 ? inlineContent : [{ type: 'text', text: ' ' }];

            return {
              type: isFirstRow ? 'tableHeader' : 'tableCell',
              content: [
                {
                  type: 'paragraph',
                  content: content
                }
              ]
            };
          });

          rows.push({
            type: 'tableRow',
            content: cells
          });

          isFirstRow = false;
        }

        if (rows.length > 0) {
          console.log('[parseMarkdown] Created table with', rows.length, 'rows');
          content.push({
            type: 'table',
            content: rows
          });
        } else {
          console.log('[parseMarkdown] WARNING: No rows created from table');
        }
      }
      continue;
    }

    // Paragraphs
    if (line.trim()) {
      const paragraphLines: string[] = [line];
      i++;

      while (i < lines.length && lines[i].trim() && !lines[i].match(/^[#>`\-*+]|^\d+\./)) {
        paragraphLines.push(lines[i]);
        i++;
      }

      const paragraphText = paragraphLines.join(' ');
      const inlineContent = parseInlineContent(paragraphText);

      // Only add paragraph if it has content
      if (inlineContent.length > 0) {
        content.push({
          type: 'paragraph',
          content: inlineContent
        });
      }
      continue;
    }

    i++;
  }

  console.log('[parseMarkdown] Result: content blocks:', content.length);
  console.log('[parseMarkdown] Content types:', content.map(c => c.type).join(', '));

  return {
    type: 'doc',
    content: content.length > 0 ? content : [{ type: 'paragraph' }]
  };
};

/**
 * Parse inline content (bold, italic, links, wikilinks, code)
 */
const parseInlineContent = (text: string): JSONContent[] => {
  // TipTap doesn't allow empty text nodes
  if (!text || text.trim() === '') return [];

  const content: JSONContent[] = [];
  let remaining = text;

  // Simple regex-based parsing (for production, use a proper markdown parser)
  const inlinePatterns = [
    { regex: /\[\[([^\]]+)\]\]/g, type: 'wikilink' }, // [[wikilink]]
    { regex: /\[([^\]]+)\]\(([^)]+)\)/g, type: 'link' }, // [text](url)
    { regex: /\*\*([^*]+)\*\*/g, type: 'bold' }, // **bold**
    { regex: /\*([^*]+)\*/g, type: 'italic' }, // *italic*
    { regex: /`([^`]+)`/g, type: 'code' }, // `code`
  ];

  // For simplicity, just return text node
  // A full implementation would parse all inline styles
  content.push({
    type: 'text',
    text: remaining
  });

  return content;
};

/**
 * Serialize TipTap JSON to markdown
 */
export const serializeToMarkdown = (json: JSONContent): string => {
  console.log('[serializeToMarkdown] Starting serialization');
  console.log('[serializeToMarkdown] Input has content?', !!json.content);

  if (!json.content) {
    console.log('[serializeToMarkdown] WARNING: No content to serialize');
    return '';
  }

  const contentTypes = json.content.map(n => n.type).join(', ');
  console.log('[serializeToMarkdown] Content types:', contentTypes);

  const result = json.content.map(node => serializeNode(node)).join('\n\n');
  console.log('[serializeToMarkdown] Result length:', result.length);
  console.log('[serializeToMarkdown] Has tables?', result.includes('|'));

  return result;
};

/**
 * Serialize a single TipTap node to markdown
 */
const serializeNode = (node: JSONContent, indent = ''): string => {
  switch (node.type) {
    case 'heading':
      const level = node.attrs?.level || 1;
      const headingText = serializeContent(node.content || []);
      return `${'#'.repeat(level)} ${headingText}`;

    case 'paragraph':
      return indent + serializeContent(node.content || []);

    case 'codeBlock':
      const language = node.attrs?.language || '';
      const code = node.content?.[0]?.text || '';
      return `\`\`\`${language}\n${code}\n\`\`\``;

    case 'bulletList':
      return (node.content || [])
        .map(item => serializeNode(item, indent + '- '))
        .join('\n');

    case 'orderedList':
      return (node.content || [])
        .map((item, idx) => serializeNode(item, indent + `${idx + 1}. `))
        .join('\n');

    case 'listItem':
      const itemContent = (node.content || [])
        .map(child => {
          if (child.type === 'paragraph') {
            return serializeContent(child.content || []);
          }
          return serializeNode(child, indent + '  ');
        })
        .join('\n');
      return indent + itemContent;

    case 'blockquote':
      return (node.content || [])
        .map(child => '> ' + serializeNode(child))
        .join('\n');

    case 'internalMarker':
      const { author = 'user', timestamp = new Date().toISOString(), type = 'note' } = node.attrs || {};
      const markerContent = (node.content || [])
        .map(child => serializeNode(child))
        .join('\n\n');
      return `<!-- MANUAL:START:${author}:${timestamp}:${type} -->\n${markerContent}\n<!-- MANUAL:END -->`;

    case 'callout':
      const calloutType = node.attrs?.type || 'info';
      const calloutContent = (node.content || [])
        .map(child => '> ' + serializeNode(child))
        .join('\n');
      return `> [!${calloutType}]\n${calloutContent}`;

    case 'table':
      return serializeTable(node);

    case 'tableRow':
      // Table rows are handled by serializeTable
      // Should not be called directly
      return '';

    case 'tableCell':
    case 'tableHeader':
      // Table cells are handled by serializeTable
      // Should not be called directly
      return '';

    case 'horizontalRule':
      return '---';

    case 'hardBreak':
      return '  \n';

    default:
      // Unknown node type, try to serialize content
      if (node.content) {
        return (node.content || []).map(child => serializeNode(child, indent)).join('');
      }
      return '';
  }
};

/**
 * Serialize inline content (text with marks)
 */
const serializeContent = (content: JSONContent[]): string => {
  return content.map(node => {
    if (node.type === 'text') {
      let text = node.text || '';
      const marks = node.marks || [];

      // Apply marks in order
      for (const mark of marks) {
        switch (mark.type) {
          case 'bold':
            text = `**${text}**`;
            break;
          case 'italic':
            text = `*${text}*`;
            break;
          case 'code':
            text = `\`${text}\``;
            break;
          case 'link':
            const href = mark.attrs?.href || '';
            text = `[${text}](${href})`;
            break;
          case 'wikilink':
            const target = mark.attrs?.target || text;
            text = `[[${target}]]`;
            break;
        }
      }

      return text;
    }

    if (node.type === 'hardBreak') {
      return '  \n';
    }

    return serializeNode(node);
  }).join('');
};

/**
 * Serialize table to markdown
 */
const serializeTable = (table: JSONContent): string => {
  const rows = table.content || [];
  if (rows.length === 0) return '';

  const lines: string[] = [];

  rows.forEach((row, rowIndex) => {
    const cells = row.content || [];
    const cellTexts = cells.map(cell => {
      // Handle both tableCell and tableHeader
      if (!cell.content || cell.content.length === 0) {
        return '';
      }

      // If the cell contains paragraphs, serialize each paragraph
      const content = cell.content.map(item => {
        if (item.type === 'paragraph') {
          return serializeContent(item.content || []);
        }
        return serializeContent([item]);
      }).join(' ');

      return content.trim();
    });

    lines.push('| ' + cellTexts.join(' | ') + ' |');

    // Add separator after first row (header)
    if (rowIndex === 0) {
      lines.push('| ' + cellTexts.map(() => '---').join(' | ') + ' |');
    }
  });

  return lines.join('\n');
};

/**
 * Helper to inject manual markers back into markdown
 */
export const injectManualMarkers = (
  markdown: string,
  markers: ManualMarker[]
): string => {
  let result = markdown;

  markers.forEach(marker => {
    const markerText = `<!-- MANUAL:START:${marker.author}:${marker.timestamp}:${marker.type} -->\n${marker.content}\n<!-- MANUAL:END -->`;
    // Simple injection - for production, use proper AST manipulation
    result = result + '\n\n' + markerText;
  });

  return result;
};
