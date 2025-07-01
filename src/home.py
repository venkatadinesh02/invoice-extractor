import streamlit as st
import pandas as pd
from image_extractor import extract_text
from ai_content_extraction import extract_invoice_data_with_gpt
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io
import json

# Page layout
st.set_page_config(page_title="AI Invoice Extractor", layout="wide")
st.title("🧾 AI Invoice & Receipt Extractor")

# File upload
uploaded_file = st.file_uploader("Upload your invoice or receipt (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    # Save uploaded file temporarily
    file_path = "temp_invoice." + uploaded_file.name.split('.')[-1]
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.write("🔍 Running Google Vision OCR...")
    ocr_text = extract_text(file_path)

    st.subheader("📄 Extracted OCR Text:")
    st.text_area("OCR Output", ocr_text, height=400)

    if st.button("🧠 Extract Structured Data using GPT-4o"):
        with st.spinner("Calling GPT-4o to structure the invoice data..."):
            structured_data = extract_invoice_data_with_gpt(ocr_text)

        st.subheader("📦 AI-Extracted Structured Data:")
        if "error" in structured_data:
            st.error("❌ " + structured_data["error"])
            st.text_area("Raw Output", structured_data.get("raw_output", ""))
        else:
            st.success("✅ Successfully extracted structured invoice data.")
            st.json(structured_data)

            st.subheader("⬇️ Download Options")

            # CSV export
            if "line_items" in structured_data and isinstance(structured_data["line_items"], list):
                df = pd.DataFrame(structured_data["line_items"])
                csv = df.to_csv(index=False).encode('utf-8')
                if st.download_button("Download Line Items as CSV", csv, "line_items.csv", "text/csv"):
                    st.success("✅ Line items CSV downloaded successfully!")
            else:
                df = pd.DataFrame([structured_data])
                csv = df.to_csv(index=False).encode('utf-8')
                if st.download_button("Download All Fields as CSV", csv, "invoice_data.csv", "text/csv"):
                    st.success("✅ All fields CSV downloaded successfully!")

            # PNG image with tabular format
            image = Image.new('RGB', (1000, 1200), color='white')
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()

            x, y = 10, 10
            row_height = 20

            for key, value in structured_data.items():
                if isinstance(value, list):
                    draw.text((x, y), f"{key}:", fill='black', font=font)
                    y += row_height
                    if value:
                        headers = value[0].keys()
                        draw.text((x + 20, y), ' | '.join(headers), fill='black', font=font)
                        y += row_height
                        for item in value:
                            row = ' | '.join(str(item.get(h, '')) for h in headers)
                            draw.text((x + 20, y), row, fill='black', font=font)
                            y += row_height
                else:
                    draw.text((x, y), f"{key}: {value}", fill='black', font=font)
                    y += row_height

            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            if st.download_button("Download as PNG", data=img_buffer, file_name="invoice_data.png", mime="image/png"):
                st.success("✅ PNG image downloaded successfully!")

            # PDF with tabular format
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)

            def write_line(line):
                pdf.multi_cell(0, 10, line)

            write_line("Invoice Data Summary:\n")
            for key, value in structured_data.items():
                if isinstance(value, list):
                    write_line(f"\n{key}:")
                    if value:
                        headers = list(value[0].keys())
                        write_line(' | '.join(headers))
                        for item in value:
                            row = ' | '.join(str(item.get(h, '')) for h in headers)
                            write_line(row)
                else:
                    write_line(f"{key}: {value}")

            pdf_data = pdf.output(dest='S').encode('latin-1')
            if st.download_button("Download as PDF", data=pdf_data, file_name="invoice_data.pdf", mime="application/pdf"):
                st.success("✅ PDF downloaded successfully!")