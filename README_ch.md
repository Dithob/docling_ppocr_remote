# 📖 Docling 远程 PP-OCR 插件（中文说明）

这是一个面向 **Docling 文档解析框架** 的第三方 **OCR 引擎插件**，可以让 Docling 通过网络请求调用 **远程 PP-OCRv5 API 服务** 进行文字识别。

该插件实现了 Docling 的 OCR 接口，并集成远程 OCR API，使 Docling 在处理图片或扫描 PDF 时能够调用你的远程 OCR 服务完成文字提取。

------

## 🔍 背景说明

Docling 是一个功能强大的开源文档解析和转换工具，支持解析 PDF、DOCX、PPTX、图像等多种格式，并提供 OCR 能力。Docling 内置了多种本地 OCR 引擎，如 EasyOCR／Tesseract／RapidOCR 等，但并不直接支持远程 OCR API。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))

为了扩展这个能力，我们实现了一个 **Remote PP-OCR 插件**，通过插件机制调用远程 OCR API 并把结果映射成 Docling 的文本单元（`TextCell`）结构，让 Docling 的文档转换 pipeline 无缝使用远程 OCR。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))

------

## 🚀 功能特点

✔ 支持远程调用 PP-OCRv5 API
✔ 与 Docling OCR 阶段无缝集成
✔ 兼容 Docling 的 OCR 管道（包括图片与 PDF）
✔ 支持可选参数配置（语言、可视化标注等）

------

## 📦 安装方法

在你要运行 Docling 的 Python 环境下执行：

```bash
git clone https://github.com/your_org/docling_ppocr_remote.git
cd docling_ppocr_remote
pip install -e .
```

确保插件 **成功安装** 到运行 Docling 的虚拟环境里，否则 Docling 无法发现和加载该插件。

------

## ⚙️ 配置与使用

### 1. 开启插件加载与远程服务支持

在构造 Docling pipeline 时，必须显式启用外部插件和远程服务：

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling_ppocr_remote.options import RemotePpOcrOptions

opt = PdfPipelineOptions()
opt.allow_external_plugins = True    # 允许加载第三方插件
opt.enable_remote_services = True    # 允许调用远程 OCR API
opt.do_ocr = True
```

------

### 2. 配置远程 OCR 接口参数

```python
opt.ocr_options = RemotePpOcrOptions(
    url="https://你的-ppocr-api/ocr",
    headers={"Authorization":"Bearer TOKEN"},
    fileType=1,        # 1=图像, 0=PDF
    visualize=False,
)
```

------

### 3. 调用示例（同时支持图像 & PDF）

```python
converter = DocumentConverter(
    format_options={
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=opt),
        InputFormat.PDF: PdfFormatOption(pipeline_options=opt),
    }
)

result = converter.convert("https://example.com/scan.png")
print(result.document.export_to_markdown())
```

这样 Docling 会自动把远程 OCR 服务的识别结果作为 OCR 引擎输出纳入文档转换流程。

------

## 🧪 docling-serve 使用示例

如果你通过 **docling-serve** 提供 HTTP 服务，请在请求 JSON 里这样设置 OCR 配置：

```json
{
  "options": {
    "allow_external_plugins": true,
    "enable_remote_services": true,
    "do_ocr": true,
    "ocr_options": {
      "kind": "ppocr_remote",
      "url": "https://你的-ppocr-api/ocr",
      "headers": {"Authorization":"Bearer TOKEN"},
      "fileType": 1,
      "visualize": false
    }
  },
  "sources": [
    {"kind":"remote_url","url":"https://example.com/scan.png"}
  ]
}
```

注意在服务端启动时需确认插件已正确安装到服务环境。

------

## 📘 参数说明

| 参数        | 类型 | 含义                                        |
| ----------- | ---- | ------------------------------------------- |
| `url`       | str  | 远程 OCR 接口地址                           |
| `headers`   | dict | HTTP 请求头（用于认证等）                   |
| `fileType`  | int  | 输入文件类型（0=PDF, 1=图像）               |
| `visualize` | bool | 是否返回可视化结果                          |
| 其他        | 可选 | PP-OCR API 支持的参数（如阈值、方向分类等） |

上述配置将被发送为 HTTP 请求体的一部分，以远程完成 OCR 识别。

------

## 📌 注意事项

✔ 插件必须安装到 Docling 运行的 Python 环境，否则无法被 Docling 发现。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))
✔ 调用远程服务需注意网络状态、超时设置等参数。
✔ `allow_external_plugins` 和 `enable_remote_services` 必须同时设置为 `True` 才能启用远程引擎。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))
✔ Docling 对 OCR 引擎的格式有校验要求，插件需符合 `BaseOcrModel` 协议。

------

## 📖 背景参考

Docling 设计了插件机制用于扩展功能，例如注册新的 OCR 引擎，你的插件通过 entrypoint 向 Docling 注册新的 OCR 实现。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))
用户必须显式开启外部插件，否则 Docling 会忽略这些扩展。([Docling](https://docling-project.github.io/docling/concepts/plugins/?utm_source=chatgpt.com))

------

## 📄 版权声明

本插件遵循你自己的开源许可（如 MIT/Apache 等），与 Docling 的许可兼容。 Docling 本身是一个开源项目，MIT 许可证可在其仓库发现。([GitHub](https://github.com/docling-project/docling?utm_source=chatgpt.com))