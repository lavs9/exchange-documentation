# How to Restart and Use TipTap Editor

## Issue
After installing new TipTap dependencies, Vite dev server needs to be restarted to recognize the packages.

## Solution: Restart the Frontend Dev Server

### Step 1: Stop the Current Dev Server
Press `Ctrl+C` in the terminal running the frontend dev server.

### Step 2: Start the Dev Server Again
```bash
cd frontend
npm run dev
```

### Step 3: Refresh Your Browser
After the server restarts, refresh your browser (Cmd+R or F5).

## Verify Installation

You can verify the packages are installed:
```bash
cd frontend
ls node_modules/@tiptap/
```

Should show:
- react
- starter-kit
- extension-link
- extension-placeholder
- extension-code-block-lowlight
- extension-table
- extension-table-row
- extension-table-cell
- extension-table-header
- And more...

## Alternative: Quick Restart Command

If you're using npm scripts, you can do:
```bash
cd /Users/mayanklavania/projects/exchange-documentation-claude/frontend
npm run dev
```

## What to Expect After Restart

1. **No more import errors** - TipTap packages will load correctly
2. **Edit button works** - Clicking "Edit Chapter" opens TipTap editor
3. **Full toolbar visible** - All formatting buttons appear
4. **Custom extensions work** - Internal markers and callouts available

## Testing the Editor

After restart:

1. Navigate to any chapter
2. Click "Edit Chapter" button (top-right)
3. You should see:
   - TipTap editor with toolbar
   - Formatting buttons (Bold, Italic, etc.)
   - 📌 Internal Marker button
   - 💡 Callout button
   - Undo/Redo buttons

4. Try inserting an internal marker:
   - Click the 📌 button
   - A light blue block appears
   - Type inside it
   - Click Save

## Troubleshooting

### If error persists after restart:

1. **Clear node_modules and reinstall:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

2. **Clear Vite cache:**
   ```bash
   cd frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

3. **Check package.json:**
   Ensure these are in your `package.json`:
   ```json
   {
     "dependencies": {
       "@tiptap/react": "^2.x.x",
       "@tiptap/starter-kit": "^2.x.x",
       "@tiptap/extension-link": "^2.x.x",
       "@tiptap/extension-placeholder": "^2.x.x",
       "@tiptap/extension-code-block-lowlight": "^2.x.x",
       "@tiptap/extension-table": "^2.x.x",
       "@tiptap/extension-table-row": "^2.x.x",
       "@tiptap/extension-table-cell": "^2.x.x",
       "@tiptap/extension-table-header": "^2.x.x",
       "@tiptap/suggestion": "^2.x.x",
       "lowlight": "^3.x.x"
     }
   }
   ```

## Common Errors and Solutions

### Error: "Cannot find module '@tiptap/react'"
**Solution:** Restart dev server

### Error: "EditorContent is not defined"
**Solution:** Check import statement, restart dev server

### Error: "lowlight is not a function"
**Solution:** Ensure lowlight is installed: `npm install lowlight`

## Quick Test Checklist

After restart, verify:
- [ ] Chapter loads without errors
- [ ] "Edit Chapter" button visible
- [ ] Clicking edit shows TipTap editor
- [ ] Toolbar has all buttons
- [ ] 📌 button creates internal marker
- [ ] 💡 button creates callout
- [ ] Save button works
- [ ] Returns to read mode after save

If all checkboxes pass, the TipTap editor is working correctly!
