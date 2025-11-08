import streamlit as st
from fpdf import FPDF
import os

st.set_page_config(page_title="완전 안전 PDF 생성기", layout="wide")
st.title("📚 Streamlit만으로 고화질 PDF 생성기")

st.write("이미지 파일 경로를 한 줄씩 입력하세요 (캡쳐 순서대로):")
image_list = st.text_area("이미지 목록", placeholder="예: image1.png\nimage2.png\nimage3.png").splitlines()

if st.button("PDF 생성"):
    valid_images = [img.strip() for img in image_list if img.strip() and os.path.exists(img.strip())]

    if not valid_images:
        st.error("유효한 이미지 파일이 없습니다.")
    else:
        pdf = FPDF(unit="pt")
        for img_path in valid_images:
            from PIL import Image
            im = Image.open(img_path)
            width, height = im.size
            pdf.add_page()
            pdf.image(img_path, x=0, y=0, w=width, h=height)
        pdf_bytes = pdf.output(dest='S').encode('latin1')

        st.success(f"✅ PDF 생성 완료! 총 {len(valid_images)} 페이지")
        st.download_button("📄 PDF 다운로드", pdf_bytes, file_name="Digital_Text
