import streamlit as st
from pathlib import Path
import tempfile
import shutil
import zipfile
import io

from PIL import Image
from hipotech_analysis.analysis_pipeline import generate_hipotech_reports

st.set_page_config(page_title="Hipotech Report Runner", layout="centered")

images_folder = Path("images_streamlit")

# Show logo and title page
col1, col2 = st.columns([1, 6])
with col1:
    st.image(f"{images_folder}/emocionado.png", width=60)
with col2:
    st.markdown("## Generador de Reportes Hipotech")

# Initialize state
for key in ["pipeline_ran", "s3_keys", "csv_path", "output_dir"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Step 1: Upload PDFs (Only show if not run yet)
if not st.session_state.pipeline_ran:

    st.header("Subir reportes Sentinel aqui")
    uploaded_files = st.file_uploader(
        "Drag and drop de los reportes en pdf aqui o click en el buscador",
        type=["pdf"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if st.button("🚀 Generar reportes"):
        if not uploaded_files:
            st.warning("⚠️ Por favor sube al menos un archivo PDF.")
        else:
            try:
                with st.spinner("⏳ Generando reportes, por favor espere..."):
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
                st.error(f"❌ Error en el procesamiento:\n{e}")

# Step 2: Show Results
elif st.session_state.pipeline_ran:

    st.success(f"✅ Listo! {len(list(st.session_state.output_dir.iterdir()))} reportes generados.")
    st.write("📂 Rutas de acceso en S3 para los PDFs generados:")
    st.write(st.session_state.s3_keys)

    # Download CSV
    if st.session_state.csv_path and Path(st.session_state.csv_path).exists():
        with open(st.session_state.csv_path, "rb") as f:
            st.download_button(
                label="📄 Descargar CSV",
                data=f,
                file_name=Path(st.session_state.csv_path).name,
                mime="text/csv"
            )
    else:
        st.warning("⚠️ Archivo CSV no encontrado para descarga.")

    # Download ZIP of PDFs
    pdf_files = list(Path(st.session_state.output_dir).glob("*.pdf"))
    if pdf_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for pdf in pdf_files:
                zipf.write(pdf, arcname=pdf.name)
        zip_buffer.seek(0)

        st.download_button(
            label="📦 Descargar todos los PDFs como ZIP",
            data=zip_buffer,
            file_name="hipotech_reports.zip",
            mime="application/zip"
        )
    else:
        st.warning("⚠️ No se encontraron archivos PDF para descargar.")

    # Reset section
    st.markdown("---")
    if st.button("🔄 Iniciar Request nuevo"):
        # Clean up temp files
        try:
            if st.session_state.csv_path:
                tmp_root = Path(st.session_state.csv_path).parent
                shutil.rmtree(tmp_root)
        except Exception as e:
            st.warning(f"⚠️ Error al limpiar los archivos temporales: {e}")
        st.session_state.clear()
        st.rerun()
