import streamlit as st
from PIL import Image
import zipfile
import io
import tempfile
import os
import math

st.set_page_config(page_title="디지털 교과서 PDF 변환기 (안전 + 다운로드 불필요)", layout="wide")
st.title("📚 자동 페이지 맞춤 + PDF 변환기 (책 페이지 기준, 안정화)")

page_width = st.number_input("책 페이지 가로 픽셀 수", min_value=100, value=1200)
page_height = st.number_input("책 페이지 세로 픽셀 수", min_value=100, value=1600)

# Step 1: ZIP 업로드
uploaded_zip = st.file_uploader("ZIP 파일 업로드 (캡쳐 순서 유지)", type="zip")

if uploaded_zip:
    temp_dir = tempfile.mkdtemp()
    image_files = []

    with zipfile.ZipFile(uploaded_zip) as zip_ref:
        image_names = [name for name in zip_ref.namelist() if name.lower().endswith(('.png', '.jpg', '.jpeg'))]
        st.write(f"{len(image_names)}개의 이미지 발견")

        for img_name in image_names:
            with zip_ref.open(img_name) as img_file:
                img_path = os.path.join(temp_dir, os.path.basename(img_name))
                img = Image.open(img_file).convert("RGB")
                img.save(img_path, format="PNG", quality=100)
                image_files.append(img_path)

    # Step 2: PDF 생성 버튼
    if st.button("PDF 생성"):
        pdf_pages = []

        for img_path in image_files:
            img = Image.open(img_path)
            img_width, img_height = img.size

            # 스크린샷이 페이지보다 작으면 확대
            scale_w = page_width / img_width if img_width < page_width else 1
            scale_h = page_height / img_height if img_height < page_height else 1
            scale = min(scale_w, scale_h)

            if scale != 1:
                img = img.resize((int(img_width*scale), int(img_height*scale)), Image.LANCZOS)
                img_width, img_height = img.size

            horizontal_pages = math.ceil(img_width / page_width)
            vertical_pages = math.ceil(img_height / page_height)

            for v in range(vertical_pages):
                for h in range(horizontal_pages):
                    left = h * page_width
                    upper = v * page_height
                    right = min((h+1) * page_width, img_width)
                    lower = min((v+1) * page_height, img_height)
                    cropped = img.crop((left, upper, right, lower))

                    # 페이지 크기보다 작으면 흰색 배경에 붙이기
                    if cropped.size != (page_width, page_height):
                        page_img = Image.new("RGB", (page_width, page_height), (255,255,255))
                        page_img.paste(cropped, (0,0))
                        pdf_pages.append(page_img)
                    else:
                        pdf_pages.append(cropped)

        if pdf_pages:
            pdf_bytes = io.BytesIO()
            pdf_pages[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pdf_pages[1:], quality=100)
            pdf_bytes.seek(0)
            st.success(f"✅ PDF 생성 완료! 총 {len(pdf_pages)}페이지")
            st.download_button("📄 PDF 다운로드", pdf_bytes, file_name="Digital_Textbook.pdf", mime="application/pdf")
