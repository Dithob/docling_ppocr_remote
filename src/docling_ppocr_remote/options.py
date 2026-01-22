from __future__ import annotations
from typing import Annotated, Any, ClassVar, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
# 你需要继承 Docling 的 OcrOptions
from docling.datamodel.pipeline_options import OcrOptions  # 具体路径按版本调整
import os


class RemotePpOcrOptions(OcrOptions):
    kind: ClassVar[Literal["tesseract"]] = "ppocr_remote"
    url: str = Field(
        default_factory=lambda: os.getenv(
            "PPOCR_REMOTE_URL",
            "https://test-ai.xiujiadian.com/zmn-paddle-ocr/ocr"
        ),
        description="Remote PP-OCRv5 endpoint",
    )
    headers: Dict[str, str] = Field(
        default_factory=lambda: (
            {"ak": os.getenv("PADDLE_PPOCR_AK")}
            if os.getenv("PADDLE_PPOCR_AK")
            else {}
        )
    )
    timeout: float = 30.0
    concurrency: int = 4
    lang: list[str] = Field(default_factory=lambda: ["english","chinese"])
    send_mode: Literal["base64", "url"] = "base64"
    fileType: Optional[int] = 1
    visualize: bool = False

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
