import streamlit as st
import img2pdf
import io
import os

st.set_page_config(page_title="프롬프트 기반 고화질 PDF 생성기", layout="wide")
st.title("📚 프롬프트 입력 + 고화질 PDF 변환기 (순수 Python)")

st.write("이미지 경로나 URL을 한 줄씩 입력하세요 (캡쳐 순서대로):")
image_list = st.text_area("이미지 목록", placeholder="예: image1.png\nimage2.png\nimage3.png").splitlines()

if st.button("PDF 생성"):
    valid_images = [img.strip() for img in image_list if img.strip() and os.path.exists(img.strip())]

    if not valid_images:
        st.error("유효한 이미지 파일이 없습니다.")
    else:
        pdf_bytes = img2pdf.convert(valid_images)
        st.success(f"✅ PDF 생성 완료! 총 {len(valid_images)} 페이지")
        st.download_button("📄 PDF 다운로드", pdf_bytes, file_name="Digital_Textbook.pdf", mime="application/pdf")
