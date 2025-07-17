import streamlit as st
from pathlib import Path
import tempfile
import shutil
import zipfile
import io

from hipotech_analysis.analysis_pipeline import generate_hipotech_reports

st.set_page_config(page_title="Hipotech Report Runner", layout="centered")
st.title("📄 Hipotech Report Runner")

# Initialize state
for key in ["pipeline_ran", "s3_keys", "csv_path", "output_dir"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Step 1: Upload PDFs (Only show if not run yet)
if not st.session_state.pipeline_ran:

    st.header("Step 1: Upload Sentinel PDF Files")
    uploaded_files = st.file_uploader(
        "Drag and drop multiple PDF files here or click to browse",
        type=["pdf"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if st.button("🚀 Run pipeline"):
        if not uploaded_files:
            st.warning("⚠️ Please upload at least one PDF file.")
        else:
            try:
                with st.spinner("⏳ Running the pipeline. Please wait..."):
                    tmp_dir = Path(tempfile.mkdtemp())
                    output_dir = tmp_dir / "hipotech_reports"
                    csv_path = tmp_dir / "credit_score_data.csv"

                    # Save uploaded files to tmp_dir
                    for file in uploaded_files:
                        file_path = tmp_dir / file.name
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                    output_dir.mkdir(parents=True, exist_ok=True)

                    s3_keys = generate_hipotech_reports(
                        tmp_dir,
                        output_dir,
                        csv_path=csv_path,
                    )

                # Set state outside the spinner to make sure it updates correctly
                st.session_state.pipeline_ran = True
                st.session_state.s3_keys = s3_keys
                st.session_state.csv_path = csv_path
                st.session_state.output_dir = output_dir

                st.rerun()  # Force rerun to show result screen

            except Exception as e:
                st.error(f"❌ Pipeline failed:\n{e}")

# Step 2: Show Results
elif st.session_state.pipeline_ran:

    st.success(f"✅ Done! Generated {len(st.session_state.s3_keys)} reports.")
    st.write("📂 S3 keys of final PDFs:")
    st.write(st.session_state.s3_keys)

    # Download CSV
    if st.session_state.csv_path and Path(st.session_state.csv_path).exists():
        with open(st.session_state.csv_path, "rb") as f:
            st.download_button(
                label="📄 Download CSV",
                data=f,
                file_name=Path(st.session_state.csv_path).name,
                mime="text/csv"
            )
    else:
        st.warning("⚠️ CSV file not found for download.")

    # Download ZIP of PDFs
    pdf_files = list(Path(st.session_state.output_dir).glob("*.pdf"))
    if pdf_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for pdf in pdf_files:
                zipf.write(pdf, arcname=pdf.name)
        zip_buffer.seek(0)

        st.download_button(
            label="📦 Download All PDFs as ZIP",
            data=zip_buffer,
            file_name="hipotech_reports.zip",
            mime="application/zip"
        )
    else:
        st.warning("⚠️ No PDF files found in the output directory.")

    # Reset section
    st.markdown("---")
    if st.button("🔄 Start New Request"):
        # Clean up temp files
        try:
            if st.session_state.csv_path:
                tmp_root = Path(st.session_state.csv_path).parent
                shutil.rmtree(tmp_root)
        except Exception as e:
            st.warning(f"⚠️ Cleanup failed: {e}")
        st.session_state.clear()
        st.rerun()
