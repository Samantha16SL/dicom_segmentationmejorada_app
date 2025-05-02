import streamlit as st
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from stl import mesh
import os

st.set_page_config(page_title="DICOM SEGMENTATION", page_icon="🧠", layout="wide")

st.title("🧠 SEGMENTACIÓN DICOM")
st.write("Bienvenido. Por favor sube tu archivo DICOM para visualizarlo, segmentarlo y exportar en STL.")

# Barra lateral para navegación
menu = st.sidebar.radio("Selecciona una opción:", ["📤 Subir DICOM", "🖼️ Visualizar Imagen", "✂️ Segmentar Imagen", "📦 Exportar STL"])

# Subir archivo DICOM
if "dicom_data" not in st.session_state:
    st.session_state.dicom_data = None
    st.session_state.image = None
    st.session_state.segmented = None

if menu == "📤 Subir DICOM":
    st.sidebar.info("Sube tu archivo DICOM para comenzar.")
    uploaded_file = st.file_uploader("Sube tu archivo DICOM", type=["dcm"])

    if uploaded_file is not None:
        dicom_data = pydicom.dcmread(uploaded_file)
        image = dicom_data.pixel_array
        st.session_state.dicom_data = dicom_data
        st.session_state.image = image
        st.success("✅ Archivo cargado exitosamente. Usa el menú de la izquierda para continuar.")

elif menu == "🖼️ Visualizar Imagen":
    if st.session_state.image is not None:
        st.subheader("Imagen DICOM Original")
        st.image(st.session_state.image, clamp=True, caption="Imagen Original")
    else:
        st.warning("⚡ Primero sube un archivo DICOM en la opción 'Subir DICOM'.")

elif menu == "✂️ Segmentar Imagen":
    if st.session_state.image is not None:
        st.subheader("Segmentación de la Imagen DICOM")
        threshold = np.mean(st.session_state.image)
        segmented = st.session_state.image > threshold
        st.session_state.segmented = segmented

        col1, col2 = st.columns(2)

        with col1:
            st.image(st.session_state.image, clamp=True, caption="Imagen Original")
        with col2:
            st.image(segmented.astype(np.uint8)*255, clamp=True, caption="Imagen Segmentada")
        
        st.success("✅ Segmentación completada.")
    else:
        st.warning("⚡ Primero sube un archivo DICOM en la opción 'Subir DICOM'.")

elif menu == "📦 Exportar STL":
    if st.session_state.segmented is not None:
        st.subheader("Exportar Segmentación a STL")

        # Crear volumen falso para STL
        volume = np.stack([st.session_state.segmented] * 5, axis=0)
        verts, faces, _, _ = measure.marching_cubes(volume, level=0)

        malla = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                malla.vectors[i][j] = verts[f[j], :]

        output_file = "exportado.stl"
        malla.save(output_file)

        st.success("✅ STL exportado exitosamente.")
        with open(output_file, "rb") as file:
            st.download_button("Descargar STL", file, file_name="exportado.stl")

        os.remove(output_file)

    else:
        st.warning("⚡ Debes segmentar una imagen primero en 'Segmentar Imagen'.")
