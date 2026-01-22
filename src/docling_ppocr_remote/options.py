# docling_ppocr_remote/options.py
from __future__ import annotations
from typing import ClassVar, Dict, Literal, Optional
from pydantic import BaseModel, Field
# 你需要继承 Docling 的 OcrOptions
from docling.datamodel.pipeline_options import OcrOptions  # 具体路径按版本调整

class RemotePpOcrOptions(OcrOptions):
    kind: ClassVar[Literal["ppocr_remote"]] = "ppocr_remote"
    url: str = Field(..., description="Remote PP-OCRv5 endpoint")
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: float = 30.0
    concurrency: int = 4
    lang: list[str] = Field(default_factory=lambda: ["english","chinese"])
    send_mode: Literal["base64", "url"] = "base64"
    fileType: Optional[int] = 1
    visualize: bool = False
    image_format: Literal["JPEG", "PNG"] = "PNG"
    jpeg_quality: int = Field(95, ge=1, le=100)
    rapidocr_compat: bool = True

    # PP-OCRv5 extra params（按你接口表补全）
    useDocOrientationClassify: Optional[bool] = None
    useDocUnwarping: Optional[bool] = None
    useTextlineOrientation: Optional[bool] = None
    textDetLimitSideLen: Optional[int] = None
    textDetLimitType: Optional[str] = None
    textDetThresh: Optional[float] = None
    textDetBoxThresh: Optional[float] = None
    textDetUnclipRatio: Optional[float] = None
    textRecScoreThresh: Optional[float] = None
