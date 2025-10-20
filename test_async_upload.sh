#!/bin/bash

# Test async document upload and status polling

echo "Testing async document upload..."
echo

# Upload document
RESPONSE=$(curl -s -X POST http://localhost:8000/api/documents/upload \
  -F "file=@sample-exchange-docs/TP_CM_Trimmed_NNF_PROTOCOL_6.2.pdf" \
  -F "title=NSE CM API Test" \
  -F "version=v6.2")

echo "Upload Response:"
echo "$RESPONSE" | jq '.'
echo

# Extract document ID
DOC_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Document ID: $DOC_ID"
echo

# Poll status every 5 seconds
echo "Polling status..."
while true; do
    STATUS=$(curl -s "http://localhost:8000/api/documents/$DOC_ID/status")
    CURRENT_STATUS=$(echo "$STATUS" | jq -r '.status')

    echo "[$(date +'%H:%M:%S')] Status: $CURRENT_STATUS"

    if [ "$CURRENT_STATUS" = "completed" ] || [ "$CURRENT_STATUS" = "failed" ]; then
        echo
        echo "Final Status:"
        echo "$STATUS" | jq '.'
        break
    fi

    sleep 5
done

echo
echo "Getting document details..."
curl -s "http://localhost:8000/api/documents/$DOC_ID" | jq '.'
