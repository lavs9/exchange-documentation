# TipTap Editor Implementation Guide

## Overview

A comprehensive TipTap-based markdown editing system for document chapters with read/edit mode toggle, custom internal markers, callout blocks, and wikilink support.

## Features Implemented

### ✅ Core Components

1. **MarkdownRenderer** (`frontend/src/components/MarkdownRenderer.tsx`)
   - Lightweight read-only markdown renderer
   - Custom rendering for internal markers, callouts, and wikilinks
   - Syntax-highlighted code blocks
   - Styled tables

2. **ChapterViewer** (`frontend/src/components/ChapterViewer.tsx`)
   - Container with read/edit mode toggle
   - Draft recovery from localStorage
   - Autosave every 30 seconds
   - Unsaved changes warning
   - Keyboard shortcuts (Cmd+S to save, Esc to cancel)

3. **TipTapEditor** (`frontend/src/components/TipTapEditor.tsx`)
   - Rich markdown editor with toolbar
   - Standard formatting (bold, italic, headings, lists)
   - Custom InternalMarker and Callout nodes
   - Code blocks with syntax highlighting
   - Tables
   - Markdown import/export

4. **DocumentViewerV2** (`frontend/src/components/DocumentViewerV2.tsx`)
   - Integration component using ChapterViewer
   - Backlinks panel
   - Context menu for creating notes
   - Wikilink navigation support

### ✅ Custom TipTap Extensions

1. **InternalMarker** (`frontend/src/extensions/InternalMarker.ts`)
   - Light blue background block for version-preserved content
   - Contains any block-level content (paragraphs, headings, lists, etc.)
   - Serializes to `<!-- MANUAL:START -->...<!-- MANUAL:END -->` format
   - Keyboard shortcut: Cmd+Shift+M
   - Displays author, timestamp, and delete button

2. **Callout** (`frontend/src/extensions/Callout.ts`)
   - Visual callout blocks with distinct styling
   - Types: info, warning, tip, note, important
   - Each type has unique color and icon
   - Type can be changed via dropdown
   - Serializes to Obsidian-style `> [!type]` blockquote syntax
   - Keyboard shortcut: Cmd+Shift+C

### ✅ Utilities

1. **Markdown Serializer/Parser** (`frontend/src/utils/tiptap-markdown.ts`)
   - Converts between TipTap JSON and markdown
   - Handles custom syntax (internal markers, callouts, wikilinks)
   - Preserves formatting

### ✅ Backend

1. **Chapter Update Endpoint** (Already implemented in `backend/app/api/documents_v2.py`)
   - `PUT /api/documents/{doc_id}/sections/{section_id}`
   - Updates chapter content in file system
   - Updates search vector
   - Marks chapter as manually edited

## Usage

### Basic Usage

Replace the old DocumentViewer with DocumentViewerV2:

```tsx
import DocumentViewerV2 from './components/DocumentViewerV2';

function App() {
  return (
    <DocumentViewerV2
      documentId="your-doc-id"
      selectedSectionId="section-id"
      showBacklinks={true}
    />
  );
}
```

### Read Mode (Default)

- Chapter displays as formatted markdown
- Internal markers show with light blue background
- Callouts display with appropriate colors and icons
- Wikilinks are clickable (purple/blue color)
- Click "Edit Chapter" button to enter edit mode

### Edit Mode

- Click "Edit Chapter" button to activate TipTap editor
- Full toolbar with formatting options
- Use toolbar buttons or keyboard shortcuts:
  - **Cmd+B**: Bold
  - **Cmd+I**: Italic
  - **Cmd+K**: Insert link
  - **Cmd+Shift+M**: Insert internal marker
  - **Cmd+Shift+C**: Insert callout
  - **Cmd+S**: Save
  - **Esc**: Cancel

### Creating Internal Markers

**From Toolbar:**
1. Click the 📌 button in toolbar
2. Content wraps in light blue block
3. Type inside the block
4. Block is preserved during version merges

**Keyboard Shortcut:**
- Press `Cmd+Shift+M`

**Result in Markdown:**
```markdown
<!-- MANUAL:START:user:2025-01-15T10:30:00Z:note -->
This content will be preserved during version updates.
<!-- MANUAL:END -->
```

### Creating Callouts

**From Toolbar:**
1. Click the 💡 button in toolbar
2. Callout block created with default type (info)
3. Use dropdown to change type: info, important, warning, tip, note
4. Type content inside callout

**Keyboard Shortcut:**
- Press `Cmd+Shift+C`

**Result in Markdown:**
```markdown
> [!important]
> This is an important callout
> with multiple lines
```

### Draft Recovery

- Editor autosaves to localStorage every 30 seconds
- If browser crashes or page reloads, draft is recovered on next visit
- Yellow banner appears: "Unsaved changes found"
- Click "Restore" to load draft or "Discard" to ignore

### Wikilinks (Read Mode)

- Wikilinks display as `[[target]]` in markdown
- Rendered as purple/blue clickable links
- Click to navigate (implementation depends on routing)

### Creating Notes from Selection

1. Select text in chapter (read mode)
2. Right-click on selection
3. Choose "Create Note from Selection"
4. Dialog opens with pre-filled content
5. Wikilink automatically inserted in source chapter

## Architecture

### Component Hierarchy

```
DocumentViewerV2
  ├── ChapterViewer (mode toggle)
  │   ├── MarkdownRenderer (read mode)
  │   └── TipTapEditor (edit mode)
  │       ├── InternalMarker extension
  │       ├── Callout extension
  │       └── Standard TipTap extensions
  ├── BacklinksPanel
  └── CreateNoteDialog
```

### Data Flow

```
1. Load Chapter
   DocumentViewerV2 → API → ChapterViewer (initialContent)

2. Edit Chapter
   ChapterViewer → TipTapEditor (markdown → JSON)

3. Save Chapter
   TipTapEditor (JSON → markdown) → ChapterViewer → API → File System

4. Read Mode
   ChapterViewer → MarkdownRenderer (custom components)
```

### Markdown Format

**Internal Marker:**
```markdown
<!-- MANUAL:START:username:2025-01-15T10:30:00Z:note -->
Content here
<!-- MANUAL:END -->
```

**Callout:**
```markdown
> [!warning]
> This is a warning callout
```

**Wikilink:**
```markdown
[[document-name]]
[[document-name#anchor]]
```

## Styling

All components use Tailwind CSS classes. Key styles:

### Internal Markers
- Background: `bg-blue-50` (very light blue)
- Border: `border-l-4 border-blue-300`
- Label: Top-right corner "Internal Note"

### Callouts
- **Info**: `bg-blue-100 border-blue-500` with 💡 icon
- **Warning**: `bg-orange-100 border-orange-500` with ⚠️ icon
- **Tip**: `bg-green-100 border-green-500` with 💡 icon
- **Note**: `bg-gray-100 border-gray-500` with 📝 icon
- **Important**: `bg-blue-100 border-blue-500` with 💡 icon

### Toolbar
- Toolbar buttons: Hover effects, active state highlighting
- Toolbar button active: `bg-blue-100 text-blue-700`

## API Integration

### Get Chapter
```typescript
GET /api/documents/{documentId}/sections/{sectionId}
Response: {
  id, title, content, page_number, file_path, ...
}
```

### Update Chapter
```typescript
PUT /api/documents/{documentId}/sections/{sectionId}
Body: { content: "markdown content" }
Response: {
  id, title, content, updated_at, ...
}
```

## Testing Checklist

### Read Mode
- [ ] Chapter renders correctly with markdown
- [ ] Internal markers show with light background
- [ ] Callouts render with correct colors and icons
- [ ] Wikilinks are styled and clickable
- [ ] Code blocks have syntax highlighting
- [ ] Tables render correctly

### Edit Mode
- [ ] "Edit" button switches to edit mode
- [ ] TipTap editor loads with correct content
- [ ] Toolbar buttons work (bold, italic, headings, lists)
- [ ] "Cancel" returns to read mode without saving
- [ ] "Save" persists changes

### Internal Markers
- [ ] Can insert marker via toolbar button
- [ ] Can insert marker via Cmd+Shift+M
- [ ] Can write content inside marker
- [ ] Marker serializes to correct markdown
- [ ] Marker parses correctly when loading chapter
- [ ] Delete button removes marker

### Callouts
- [ ] Can insert callout via toolbar button
- [ ] Can insert callout via Cmd+Shift+C
- [ ] Dropdown changes callout type
- [ ] Each type has correct styling
- [ ] Callout serializes to Obsidian syntax
- [ ] Callout parses correctly

### Save/Draft
- [ ] Save button persists changes
- [ ] Autosave works (check localStorage)
- [ ] Draft recovery banner appears
- [ ] Restore draft works
- [ ] Discard draft clears localStorage
- [ ] Unsaved changes warning works

## Known Limitations

1. **Wikilink Autocomplete**: Not yet implemented. Users must type wikilinks manually.
2. **Slash Commands**: Not yet implemented. Use toolbar buttons instead.
3. **Nested Internal Markers**: Cannot nest markers inside markers (by design).
4. **Complex Tables**: Table editing is basic. For complex tables, edit in markdown.
5. **Markdown Parser**: Simplified parser. Some edge cases may not parse correctly.

## Future Enhancements

### Optional Features (Not Yet Implemented)

1. **Wikilink Autocomplete** (Task 7)
   - Trigger on typing `[[`
   - Show dropdown with all chapters/notes
   - Filter as user types
   - Insert wikilink on selection

2. **Slash Commands** (Task 9)
   - Trigger on typing `/`
   - Menu with all block types
   - Quick insertion of headings, callouts, markers, etc.

3. **Drag and Drop**
   - Reorder blocks via drag handles
   - Requires additional extension

4. **Collaborative Editing**
   - Multi-user editing with Y.js
   - Real-time collaboration

5. **Version Comparison**
   - Visual diff between versions
   - Highlight internal markers that were preserved

## Troubleshooting

### Editor Not Loading
- Check browser console for errors
- Verify all TipTap dependencies are installed
- Check that `TipTapEditor.css` is imported

### Markdown Not Serializing Correctly
- Check `tiptap-markdown.ts` serializer
- Verify custom nodes (InternalMarker, Callout) are registered
- Test with simple content first

### Styles Not Applying
- Ensure Tailwind CSS is configured
- Check that CSS classes are not being purged
- Verify `TipTapEditor.css` is imported

### Autosave Not Working
- Check localStorage is enabled
- Verify draft key format: `chapter-draft-{chapterId}`
- Check browser console for errors

## Migration from Old Editor

If you're migrating from the old MarkdownEditor to the new TipTap system:

1. Replace `DocumentViewer` with `DocumentViewerV2` in your app
2. Update any direct MarkdownEditor imports to use ChapterViewer
3. Test all editing workflows
4. Verify markdown serialization for existing chapters
5. Update any custom styling to match new components

## Support

For issues or questions:
- Check the TipTap documentation: https://tiptap.dev
- Review component source code in `frontend/src/components/`
- Review extension source code in `frontend/src/extensions/`
- Check backend API in `backend/app/api/documents_v2.py`
