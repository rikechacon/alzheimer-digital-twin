# Alzheimer Digital Twin (ADT) 🧠

Proyecto de Gemelo Digital para el modelado y predicción de la progresión del Alzheimer.

## 🏗️ Arquitectura del Sistema
```mermaid
graph TD
    A[Datos del Paciente] --> B{Motor ADT}
    B --> C[Modelo Biológico]
    B --> D[Simulaciones de Progresión]
    C --> E[Visualización / Dashboard]
    D --> F[Reporte de Predicción]
```

## 📂 Estructura del Proyecto
* `src/`: Lógica principal del gemelo digital.
* `data/`: Almacenamiento de datasets (ignorado por Git).
* `notebooks/`: Experimentos y análisis exploratorio.
* `tests/`: Pruebas unitarias para validar los modelos.

## 🚀 Instalación
```bash
pip install -r requirements.txt
```
