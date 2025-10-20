import json
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = (
    TableFormerMode.ACCURATE
)  # use more accurate TableFormer model

# Sample PDF source: Use a local path or a public URL for testing
# For example, a public arXiv PDF as shown in Docling docs
source = "/Users/mayanklavania/projects/exchange-documentation/exchange-api/nse/TP_CM_Trimmed_NNF_PROTOCOL_6.1_1.pdf"  # Replace with your exchange API PDF path, e.g., "/path/to/nse_api_doc.pdf"

# Initialize the converter
doc_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
# converter = DocumentConverter()

# Convert the PDF
result = doc_converter.convert(source)

# Extract Markdown
markdown_content = result.document.export_to_markdown()
print("Extracted Markdown:")
# print(markdown_content)

html_content = result.document.export_to_html()
print("Extracted HTML:")
# print(markdown_content)

# Extract the Docling document as structured JSON
doc_dict = result.document.export_to_dict()
json_content = json.dumps(doc_dict, indent=4)
print("\nExtracted Docling Document as JSON:")
# print(json_content)

# Optionally, save to files
with open("output.md", "w", encoding="utf-8") as md_file:
    md_file.write(markdown_content)

with open("output.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_content)

with open("output.html", "w", encoding="utf-8") as html_file:
    html_file.write(html_content)
