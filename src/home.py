import streamlit as st
import pandas as pd
from image_extraction import extract_text

# Page title
st.title("AI Invoice & Receipt Extractor")

# File upload
uploaded_file = st.file_uploader("Upload your invoice or receipt (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])


# Process file
if uploaded_file is not None:
    st.success("File uploaded successfully!")

    file_path = "temp_invoice." + uploaded_file.name.split('.')[-1]

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.write("Running Google Vision OCR...")
    ocr_text = extract_text(file_path)

    st.subheader("Extracted Text:")
    st.text_area("OCR Output:", ocr_text, height=400)







    # # Show extracted data
    # st.subheader("Extracted Invoice Data")
    # st.table(extracted_df)
    #
    # # Download extracted data
    # csv = extracted_df.to_csv(index=False).encode('utf-8')
    # st.download_button(
    #     label="Download Extracted Data as CSV",
    #     data=csv,
    #     file_name='extracted_invoice_data.csv',
    #     mime='text/csv',
    # )
