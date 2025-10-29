-- Fix chapter file paths after renaming
-- Chapters 9 and 10 had truncated filenames in the database

UPDATE chapters 
SET file_path = 'nse-nnf-protocol/versions/v6.1/chapters/chapter-09-chapter-9-encryption-decryption-of-interactive-messages.md'
WHERE chapter_number = 9 
AND file_path LIKE '%chapter-09%encryption-decryption-of-interactive-mes.md';

UPDATE chapters 
SET file_path = 'nse-nnf-protocol/versions/v6.1/chapters/chapter-10-chapter-10-direct-interface-to-exchange-trading-system.md'
WHERE chapter_number = 10 
AND file_path LIKE '%chapter-10%direct-interface-to-exchange-trading-sy.md';

-- Verify the updates
SELECT chapter_number, file_path 
FROM chapters 
WHERE chapter_number IN (9, 10) 
ORDER BY chapter_number;
