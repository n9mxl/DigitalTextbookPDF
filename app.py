import streamlit as st
from PIL import Image
import zipfile
import io
import tempfile
import os
import math

st.set_page_config(page_title="디지털 교과서 PDF 변환기", layout="wide")
st.title("📚 자동 페이지 맞춤 + PDF 변환기 (책 페이지 기준)")

uploaded_zip = st.file_uploader("ZIP 파일 업로드 (캡쳐 순서 유지)", type="zip")
page_width = st.number_input("책 페이지 가로 픽셀 수", min_value=100, value=1200)
page_height = st.number_input("책 페이지 세로 픽셀 수", min_value=100, value=1600)

if uploaded_zip and page_width > 0 and page_height > 0:
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(uploaded_zip) as zip_ref:
            image_names = [name for name in zip_ref.namelist() if name.lower().endswith(('.png', '.jpg', '.jpeg'))]
            st.write(f"{len(image_names)}개의 이미지 발견")
            
            pdf_pages = []
            
            for img_name in image_names:
                with zip_ref.open(img_name) as img_file:
                    img = Image.open(img_file)
                    img = img.convert("RGB")
                    img_width, img_height = img.size
                    
                    # 스크린샷이 페이지보다 작으면 확대
                    scale_w = page_width / img_width if img_width < page_width else 1
                    scale_h = page_height / img_height if img_height < page_height else 1
                    scale = min(scale_w, scale_h)
                    
                    if scale != 1:
                        new_w = int(img_width * scale)
                        new_h = int(img_height * scale)
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                        img_width, img_height = img.size
                    
                    # 몇 페이지로 나누어야 하는지 계산
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
                                page_img = Image.new("RGB", (page_width, page_height), (255, 255, 255))
                                page_img.paste(cropped, (0,0))
                                pdf_pages.append(page_img)
                            else:
                                pdf_pages.append(cropped)
            
            if pdf_pages:
                pdf_bytes = io.BytesIO()
                pdf_pages[0].save(
                    pdf_bytes,
                    format="PDF",
                    save_all=True,
                    append_images=pdf_pages[1:],
                    quality=100
                )
                pdf_bytes.seek(0)
                
                st.success(f"✅ PDF 생성 완료! 총 {len(pdf_pages)}페이지")
                st.download_button(
                    label="📄 PDF 다운로드",
                    data=pdf_bytes,
                    file_name="Digital_Textbook.pdf",
                    mime="application/pdf"
                )
