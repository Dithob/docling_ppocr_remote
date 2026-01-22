# Docling Remote PP-OCR Plugin

A third-party **Docling OCR engine plugin** that enables Docling to call a **remote PP-OCRv5 API service** for OCR, providing high-quality text extraction from images and scanned documents.

This plugin lets you seamlessly use a remote OCR service within Docling’s document conversion pipelines (PDFs and images) as an alternative to local OCR backends like RapidOCR, EasyOCR, etc.

------

## 🧠 Overview

Docling is an open-source document parsing and conversion toolkit that can process PDFs, DOCX, images, and other formats into structured representations such as Markdown or JSON. ([GitHub](https://github.com/docling-project/docling/blob/main/README.md?utm_source=chatgpt.com))

This plugin implements a custom Docling OCR engine that:

- Sends image crops to a **remote PP-OCR API** endpoint
- Parses and maps the returned text/boxes into Docling’s `TextCell` data model
- Integrates into Docling’s OCR stage via the plugin mechanism

------

## 📦 Features

- Remote network OCR integration, useful when local OCR models are unavailable
- Supports **PP-OCRv5 API**-compatible services
- Works with Docling converter pipelines (`DocumentConverter`)
- Compatible with **Docling Server (docling-serve)**

------

## 🚀 Installation

1. **Clone the plugin repo**

   ```bash
   git clone https://github.com/your_org/docling_ppocr_remote.git
   cd docling_ppocr_remote
   ```

2. **Install the plugin into your Python environment**

   ```bash
   pip install -e .
   ```

3. Make sure Docling and docling-serve are installed:

   ```bash
   pip install docling docling-serve
   ```

> This plugin uses Python’s editable install (`pip install -e .`) so you can edit and test locally.

------

## 🧩 How It Works

Docling discovers plugins via the **entry point** registered in your `pyproject.toml`.
When enabled, this plugin becomes one of the OCR engines Docling can choose at runtime.

The plugin implements:

- A custom `RemotePpOcrOptions` class defining remote OCR configuration
- A `RemotePpOcrModel` that calls your remote PP-OCR API
- Integration into Docling’s OCR stage (`BaseOcrModel`)

------

## 📌 Usage Example (Python)

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling_ppocr_remote.options import RemotePpOcrOptions

# Configure Docling pipeline
opt = PdfPipelineOptions()
opt.allow_external_plugins = True   # enable plugin loading
opt.enable_remote_services = True   # allow remote OCR services
opt.do_ocr = True

# Set your remote OCR service
opt.ocr_options = RemotePpOcrOptions(
    url="https://your-ppocrv5/api/ocr",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    fileType=1,       # 1 = image, 0 = PDF
    visualize=False
)

# Use IMAGE and PDF options
converter = DocumentConverter(
    format_options={
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=opt),
        InputFormat.PDF: PdfFormatOption(pipeline_options=opt),
    }
)

result = converter.convert("https://example.com/scan.png")
print(result.document.export_to_markdown())
```

------

## 🧪 docling-serve Example (HTTP JSON)

If you’re using `docling-serve` as a server, send:

```json
{
  "options": {
    "allow_external_plugins": true,
    "enable_remote_services": true,
    "do_ocr": true,
    "do_table_structure": true,
    "ocr_engine": "ppocr_remote",
    "ocr_options": {
      "kind": "ppocr_remote",
      "url": "https://your-ppocrv5/api/ocr",
      "headers": {"Authorization": "Bearer YOUR_TOKEN"},
      "fileType": 1,
      "visualize": false
    }
  },
  "sources": [
    {"kind": "remote_url", "url": "https://example.com/scan.png"}
  ]
}
```

Make sure the server is started with external plugin support and the plugin is installed in its environment.
If `ocr_options` are omitted, the remote engine cannot contact your service, and results can diverge from RapidOCR.

------

## 📌 Plugin Options Explained

| Option                  | Type    | Description                            |
| ----------------------- | ------- | -------------------------------------- |
| `url`                   | str     | Remote OCR API endpoint                |
| `headers`               | dict    | Custom HTTP headers (e.g., auth)       |
| `fileType`              | int     | 0 = PDF, 1 = image                     |
| `visualize`             | bool    | Whether to return annotated image      |
| `image_format`          | str     | Image encoding for upload (`PNG`/`JPEG`) |
| `jpeg_quality`          | int     | JPEG quality if using `JPEG`           |
| `rapidocr_compat`       | bool    | Match RapidOCR-style text normalization and defaults |
| other PP-OCR parameters | various | Control detection/recognition behavior |

Check your remote OCR API documentation for full parameter support.

------

## ❗ Requirements

- Python ≥ 3.10
- Docling ≥ (compatible version)
- Docling Serve if used as a service API

------

## ✅ Troubleshooting

- **Plugin not loading?**
  Ensure `allow_external_plugins=True` and the plugin is installed into the same environment as Docling.
- **Remote requests failing?**
  Check endpoint URL, headers, and API network permissions.

------

## 📜 License

This plugin is typically licensed under **MIT** (or your chosen license).
Include license file in the project root.

------

## 📌 References

- Docling official documentation and examples — Python API, plugin system. ([GitHub](https://github.com/docling-project/docling/blob/main/README.md?utm_source=chatgpt.com))
- Docling serve API reference (parameters, options). ([PyPI](https://pypi.org/project/docling-serve/0.3.0/?utm_source=chatgpt.com))
