from __future__ import annotations
import base64
import io
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image
import fitz  # PyMuPDF

# -------- Config --------
@dataclass
class DescribeConfig:
    provider: str = "openai"          # "openai" | "gemini"
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-1.5-flash-latest"
    max_pages: int = 2                 # cap pages to describe
    pdf_dpi: int = 180                 # render quality
    text_len_threshold: int = 50       # treat page as image if extracted text is below this
    describe_prompt: str = (
        "You are a concise visual analyst. "
        "Describe the image like a human would: what it depicts, layout, key elements, and any visible labels. "
        "Avoid reading or quoting long text; focus on the visual content, structures, symbols, and their relationships. "
        "Keep it under 150 words per image."
    )

# -------- Helpers --------
def _image_to_png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()

def _bytes_to_data_url_png(b: bytes) -> str:
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def _is_image_ext(p: Path) -> bool:
    ext = p.suffix.lower()
    return ext in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".gif"}

def _probe_mime(p: Path) -> str:
    m, _ = mimetypes.guess_type(str(p))
    return m or "application/octet-stream"

def _render_pdf_pages_as_pngs(pdf_path: Path, dpi: int, max_pages: int, text_len_threshold: int) -> List[Tuple[int, bytes]]:
    """
    Render visually-relevant PDF pages to PNG bytes, up to max_pages.
    Heuristic: prefer pages with low text density (visual drawings, maps, plans).
    """
    images: List[Tuple[int, bytes]] = []
    with fitz.open(str(pdf_path)) as doc:
        # Score pages by "visuality": short extracted text → more visual
        scored_pages = []
        for i, page in enumerate(doc):
            # lightweight text check (only for decision; we won't use it for description)
            text = page.get_text("text") or ""
            score = len(text.strip())
            scored_pages.append((i, score))
        # sort ascending by text length (more visual first)
        scored_pages.sort(key=lambda t: t[1])

        for idx, score in scored_pages[:max_pages]:
            page = doc.load_page(idx)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            png_bytes = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).tobytes()
            # Convert raw RGB bytes -> PNG properly
            pil_im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append((idx, _image_to_png_bytes(pil_im)))
    return images

# -------- Providers --------
def _describe_images_openai(png_bytes_list: List[Tuple[int, bytes]], cfg: DescribeConfig) -> List[Tuple[int, str]]:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    results: List[Tuple[int, str]] = []
    for page_idx, b in png_bytes_list:
        data_url = _bytes_to_data_url_png(b)
        msg = [
            {"role": "system", "content": "You describe images objectively and succinctly."},
            {"role": "user", "content": [
                {"type": "text", "text": cfg.describe_prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ]
        resp = client.chat.completions.create(
            model=cfg.openai_model,
            messages=msg,
            temperature=0.2,
        )
        desc = resp.choices[0].message.content.strip()
        results.append((page_idx, desc))
    return results

def _describe_images_gemini(png_bytes_list: List[Tuple[int, bytes]], cfg: DescribeConfig) -> List[Tuple[int, str]]:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(cfg.gemini_model)

    results: List[Tuple[int, str]] = []
    for page_idx, b in png_bytes_list:
        # gemini takes raw bytes with MIME
        img_part = {"mime_type": "image/png", "data": b}
        resp = model.generate_content([cfg.describe_prompt, img_part])
        results.append((page_idx, (resp.text or "").strip()))
    return results

# -------- Main entry --------
def describe_visual_file(file_path: str, cfg: Optional[DescribeConfig] = None) -> List[Tuple[str, str]]:
    """
    Decide if the file is visual, render if needed, and get a human-style description
    via a multimodal LLM. Returns list of (label, description) where label is
    'image' or 'page {n}'.
    """
    cfg = cfg or DescribeConfig()
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(file_path)

    # 1) If it's an image, just send the image
    if _is_image_ext(p) or (_probe_mime(p).startswith("image/")):
        im = Image.open(str(p)).convert("RGB")
        b = _image_to_png_bytes(im)
        pngs = [(-1, b)]  # -1 for single image
    # 2) If it's a PDF, render visually-relevant pages
    elif p.suffix.lower() == ".pdf":
        pngs = _render_pdf_pages_as_pngs(
            p, dpi=cfg.pdf_dpi, max_pages=cfg.max_pages, text_len_threshold=cfg.text_len_threshold
        )
        if not pngs:
            raise RuntimeError("Could not render any PDF pages")
    else:
        # Non-visual types are skipped
        raise ValueError(f"Unsupported or non-visual type: {p.suffix}")

    # 3) Call provider
    if cfg.provider == "openai":
        results = _describe_images_openai(pngs, cfg)
    elif cfg.provider == "gemini":
        results = _describe_images_gemini(pngs, cfg)
    else:
        raise ValueError("provider must be 'openai' or 'gemini'")

    # 4) Format return
    out: List[Tuple[str, str]] = []
    for page_idx, desc in results:
        label = "image" if page_idx < 0 else f"page {page_idx+1}"
        out.append((label, desc))
    return out

# ---- Example usage ----
if __name__ == "__main__":
    cfg = DescribeConfig(provider="openai", max_pages=1, pdf_dpi=200)
    # Example: your campus sheet PDF (replace with your path)
    target = "DocLabs_Sample_Project_Template/01. Project Information/BW Tank Fencing and Disconnect/A-B-01_SI-186.pdf"
    for label, text in describe_visual_file(target, cfg):
        print(f"[{label}] {text}\n")
