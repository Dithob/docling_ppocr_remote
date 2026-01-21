# docling_ppocr_remote/model.py
from __future__ import annotations
import base64, io
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Optional, Type

import httpx
from PIL import Image

from docling.models.base_ocr_model import BaseOcrModel  # 具体路径按版本调整
from docling.datamodel.document import Page  # 按版本调整
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import TextCell, BoundingRectangle
from docling.datamodel.document import ConversionResult  # 按版本调整
from docling.datamodel.pipeline_options import AcceleratorOptions  # 按版本调整
from .options import RemotePpOcrOptions

def _pil_to_b64(img: Image.Image, fmt="JPEG", quality=90) -> str:
    buf = io.BytesIO()
    save_kwargs = {}
    if fmt.upper() == "JPEG":
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    img.save(buf, format=fmt, **save_kwargs)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

class RemotePpOcrModel(BaseOcrModel):
    def __init__(
        self,
        enabled: bool,
        artifacts_path,
        options: RemotePpOcrOptions,
        accelerator_options: AcceleratorOptions,
    ):
        super().__init__(enabled=enabled, artifacts_path=artifacts_path, options=options, accelerator_options=accelerator_options)
        self._opt: RemotePpOcrOptions = options
        self._client = httpx.Client(timeout=self._opt.timeout)

    @classmethod
    def get_options_type(cls) -> Type[RemotePpOcrOptions]:
        return RemotePpOcrOptions

    def _call_remote(self, img: Image.Image) -> dict:
        payload = {
            "fileType": self._opt.fileType,
            "visualize": self._opt.visualize,
            # 下面把可选参数按“非 None 才传”拼进去
        }
        for k in [
            "useDocOrientationClassify","useDocUnwarping","useTextlineOrientation",
            "textDetLimitSideLen","textDetLimitType","textDetThresh","textDetBoxThresh",
            "textDetUnclipRatio","textRecScoreThresh",
        ]:
            v = getattr(self._opt, k)
            if v is not None:
                payload[k] = v

        if self._opt.send_mode == "base64":
            payload["file"] = _pil_to_b64(img, fmt="JPEG")
        else:
            raise ValueError("send_mode=url requires a reachable URL; prefer base64 in docling-serve")

        r = self._client.post(self._opt.url, json=payload, headers=self._opt.headers)
        r.raise_for_status()
        return r.json()

    def _ppocr_to_cells_backup(self, pruned: dict, rect_offset_xy=(0.0, 0.0)) -> List[TextCell]:
        # 兼容 rec_polys / rec_boxes 两种
        texts = pruned.get("rec_texts", []) or []
        polys = pruned.get("rec_polys", []) or []
        boxes = pruned.get("rec_boxes", []) or []

        ox, oy = rect_offset_xy
        out: List[TextCell] = []

        def box_from_poly(poly):
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            return min(xs), min(ys), max(xs), max(ys)

        for i, txt in enumerate(texts):
            if not txt:
                continue

            if i < len(boxes) and boxes[i]:
                l, t, r, b = boxes[i]
            elif i < len(polys) and polys[i]:
                l, t, r, b = box_from_poly(polys[i])
            else:
                continue

            bb = BoundingBox(
                l=l + ox, t=t + oy, r=r + ox, b=b + oy,
                coord_origin=CoordOrigin.TOPLEFT,
            )
            tc = TextCell(
                index=i,
                text=txt,
                rect=bb,  # 具体字段按 TextCell 版本
                from_ocr=True,
            )
            out.append(tc)

        return out


    def _ppocr_to_cells(self, pruned: dict, rect_offset_xy=(0.0, 0.0)) -> List[TextCell]:
        texts = pruned.get("rec_texts") or []
        boxes = pruned.get("rec_boxes") or []
        polys = pruned.get("rec_polys") or []
        scores = pruned.get("rec_scores") or []

        ox, oy = rect_offset_xy
        out: List[TextCell] = []

        def box_from_poly(poly):
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            return min(xs), min(ys), max(xs), max(ys)

        for i, txt in enumerate(texts):
            if not txt:
                continue

            if i < len(boxes) and boxes[i]:
                l, t, r, b = boxes[i]
            elif i < len(polys) and polys[i]:
                l, t, r, b = box_from_poly(polys[i])
            else:
                continue

            conf = float(scores[i]) if i < len(scores) and scores[i] is not None else None

            bbox = BoundingBox.from_tuple(
                coord=(l + ox, t + oy, r + ox, b + oy),
                origin=CoordOrigin.TOPLEFT,
            )
            rect = BoundingRectangle.from_bounding_box(bbox)

            out.append(
                TextCell(
                    index=i,
                    text=txt,
                    orig=txt,  # RapidOCR 也是这么填的
                    confidence=conf,  # 可选，但强烈建议填
                    from_ocr=True,
                    rect=rect,
                )
            )
        return out

    def __call__(self, conv_res: ConversionResult, page_batch: Iterable[Page]) -> Iterable[Page]:
        # 这里建议加：若 conv_res.options.enable_remote_services=False -> raise OperationNotAllowed
        pages = list(page_batch)
        for page in pages:
            if not self.enabled:
                yield page
                continue
            if page.image is None or page.size is None:
                yield page
                continue

            ocr_rects = self.get_ocr_rects(page)  # 基类提供:contentReference[oaicite:13]{index=13}
            futures = []
            with ThreadPoolExecutor(max_workers=self._opt.concurrency) as ex:
                for rect in ocr_rects:
                    crop = page.image.crop(tuple(rect.as_tuple()))  # PIL crop
                    futures.append((rect, ex.submit(self._call_remote, crop)))

                all_ocr_cells: List[TextCell] = []
                for rect, fut in futures:
                    data = fut.result()
                    ocr_results = (data.get("result") or {}).get("ocrResults") or []
                    if not ocr_results:
                        continue
                    pruned = (ocr_results[0].get("prunedResult") or {})
                    cells = self._ppocr_to_cells(pruned, rect_offset_xy=(rect.l, rect.t))
                    all_ocr_cells.extend(cells)

            # 用基类的后处理把 OCR cells 合并/过滤/重排写回 parsed_page:contentReference[oaicite:14]{index=14}
            # self.post_process_cells(conv_res, page, all_ocr_cells, ocr_rects)
            self.post_process_cells(all_ocr_cells, page)
            yield page
