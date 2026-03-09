import streamlit as st
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import xarray as xr
import yaml
import cdsapi
import gc

# Page configuration
st.set_page_config(
    page_title="ERA5 WAM2Layers Workflow",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 ERA5 Data Processing & WAM2Layers Execution")
st.markdown("Automated workflow for downloading ERA5 data, preprocessing, and running WAM2Layers atmospheric trajectory calculations.")

# Sidebar for inputs
st.sidebar.header("📋 Configuration Parameters")

# Date inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
with col2:
    end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-02"))

# Other parameters
st.sidebar.subheader("Download Settings")
skip_existing = st.sidebar.checkbox("Skip existing files", value=True)
grid_resolution = st.sidebar.selectbox("Grid Resolution", ["0.25x0.25", "0.5x0.5"], index=0)
grid = [float(x) for x in grid_resolution.split('x')]

# Area selection
st.sidebar.subheader("Geographic Area")
use_global = st.sidebar.checkbox("Global coverage", value=True)
if not use_global:
    st.sidebar.markdown("**Custom Area (N/W/S/E):**")
    area_n = st.sidebar.number_input("North", value=90.0, min_value=-90.0, max_value=90.0)
    area_w = st.sidebar.number_input("West", value=-180.0, min_value=-180.0, max_value=180.0)
    area_s = st.sidebar.number_input("South", value=-90.0, min_value=-90.0, max_value=90.0)
    area_e = st.sidebar.number_input("East", value=180.0, min_value=-180.0, max_value=180.0)
    area = [area_n, area_w, area_s, area_e]
else:
    area = None

# Variables selection
st.sidebar.subheader("Variables to Process")
ml_vars = st.sidebar.multiselect("Model Level Variables", ["u", "v", "q"], default=["u", "v", "q"])
surface_vars = st.sidebar.multiselect("Surface Variables", ["tp", "e", "sp", "tcw"], default=["tp", "sp", "e", "tcw"])

# Output directories
st.sidebar.subheader("Output Directories")
target_dir = st.sidebar.text_input("Data Directory", value=".")
preprocessed_dir = st.sidebar.text_input("Preprocessed Data Directory", value="./preprocessed_data")
output_dir = st.sidebar.text_input("WAM2Layers Output Directory", value="./output_data")

# Action buttons
st.sidebar.header("🚀 Actions")
run_download = st.sidebar.button("📥 Download ERA5 Data", type="primary")
run_preprocess = st.sidebar.button("⚙️ Preprocess Data")
run_wam2layers = st.sidebar.button("🌪️ Run WAM2Layers")
run_full_workflow = st.sidebar.button("🎯 Run Full Workflow", type="primary")

# Main content area
st.header("📊 Workflow Status")

# Status placeholders
status_placeholder = st.empty()
progress_placeholder = st.empty()
log_placeholder = st.empty()

# Initialize session state for logs
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message):
    """Add a message to the log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    log_placeholder.text_area("📝 Execution Log", value="\n".join(st.session_state.logs[-50:]), height=300)

def clear_logs():
    """Clear the log"""
    st.session_state.logs = []
    log_placeholder.empty()

# Convert dates to strings
START_DATE = start_date.strftime("%Y-%m-%d")
END_DATE = end_date.strftime("%Y-%m-%d")

# Parse dates
start = pd.to_datetime(START_DATE)
end = pd.to_datetime(END_DATE)
year = start.year

# Generate date range
datelist = pd.date_range(START_DATE, END_DATE)
months = list(set([str(d.month).zfill(2) for d in datelist]))
months.sort()

# Days per month
days_all = {}
dates = []
for month in months:
    month_days = datelist[datelist.month == int(month)]
    days_all[month] = [str(d.day).zfill(2) for d in month_days]
    month_str = month
    start_day = min(month_days).strftime("%d")
    end_day = max(month_days).strftime("%d")
    dates.append(f"{year}-{month}-{start_day}/to/{year}-{month}-{end_day}")

# Variables dictionaries
ml_variables = {var: {"u": 131, "v": 132, "q": 133}[var] for var in ml_vars}
surface_variables = {var: {
    "tp": "total_precipitation",
    "e": "evaporation", 
    "sp": "surface_pressure",
    "tcw": "total_column_water"
}[var] for var in surface_vars}

# Levels and times
levels = "20/40/60/80/90/95/100/105/110/115/120/123/125/128/130/131/132/133/134/135/136/137"
times = [f"{h:02d}:00" for h in range(24)]

def download_era5_data():
    """Download ERA5 data from CDS API"""
    add_log("="*80)
    add_log("INICIANDO DESCARGA DE DATOS ERA5")
    add_log("="*80)

    try:
        # Initialize CDS client
        c = cdsapi.Client(timeout=600, quiet=False)
        
        progress_bar = progress_placeholder.progress(0)
        total_steps = len(months) * (len(surface_vars) + len(ml_vars))
        current_step = 0

        for month in months:
            outfolder = Path(target_dir) / f"{year}" / f"{month}"
            outfolder.mkdir(exist_ok=True, parents=True)
            
            this_days = days_all[month]
            
            # Download surface variables
            add_log(f"--- Descargando variables de superficie para mes {month} ---")
            for variable, long_name in surface_variables.items():
                outfile = f"ERA5_{year}-{month}_{variable}.nc"
                filepath = outfolder / outfile
                
                if filepath.exists() and skip_existing:
                    add_log(f"✓ {filepath} ya existe, saltando.")
                else:
                    try:
                        add_log(f"Descargando {variable}...")
                        request = {
                            "product_type": "reanalysis",
                            "variable": long_name,
                            "year": f"{year}",
                            "month": month,
                            "day": this_days,
                            "time": times,
                            "grid": grid,
                            "format": "netcdf",
                        }
                        if area:
                            request["area"] = area
                            
                        c.retrieve("reanalysis-era5-single-levels", request, str(filepath))
                        add_log(f"✓ Descargado: {filepath}")
                    except Exception as e:
                        add_log(f"✗ Error descargando {variable} mes {month}: {e}")
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
            
            # Download model level variables
            add_log(f"--- Descargando variables de modelo para mes {month} ---")
            for variable, param in ml_variables.items():
                outfile = f"ERA5_{year}-{month}_ml_{variable}.nc"
                filepath = outfolder / outfile
                
                if filepath.exists() and skip_existing:
                    add_log(f"✓ {filepath} ya existe, saltando.")
                else:
                    try:
                        add_log(f"Descargando ml_{variable}...")
                        request = {
                            "time": times,
                            "dates": dates[int(month)-1],
                            "levelist": levels,
                            "param": param,
                            "class": "ea",
                            "expver": "1",
                            "levtype": "ml",
                            "stream": "oper",
                            "type": "an",
                            "format": "netcdf",
                            "grid": grid,
                        }
                        if area:
                            request["area"] = area
                            
                        c.retrieve("reanalysis-era5-complete", request, str(filepath))
                        add_log(f"✓ Descargado: {filepath}")
                    except Exception as e:
                        add_log(f"✗ Error descargando ml_{variable} mes {month}: {e}")
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)

        add_log("✓ DESCARGA COMPLETADA")
        return True
        
    except Exception as e:
        add_log(f"✗ Error en descarga: {e}")
        return False

def preprocess_data():
    """Preprocess and decompose ERA5 data"""
    add_log("="*80)
    add_log("INICIANDO PREPROCESAMIENTO Y DESCOMPOSICIÓN")
    add_log("="*80)

    try:
        # Create preprocessing directory
        output_base_dir = Path(preprocessed_dir) / "descompuestos"
        output_base_dir.mkdir(exist_ok=True, parents=True)

        progress_bar = progress_placeholder.progress(0)
        total_months = len(months)
        current_month = 0

        for month in months:
            mes_str = f"{month:0>2}"
            mes_path = Path(target_dir) / f"{year}" / mes_str

            if not mes_path.exists():
                add_log(f"✗ Carpeta {mes_path} no encontrada.")
                continue

            # Create output folder for month
            output_dir = output_base_dir / mes_str
            output_dir.mkdir(exist_ok=True, parents=True)

            add_log(f"--- Procesando mes {mes_str} ---")

            # Process surface variables
            for var in surface_vars:
                archivo_mensual = mes_path / f"ERA5_{year}-{mes_str}_{var}.nc"
                if not archivo_mensual.exists():
                    add_log(f"  ℹ Archivo {archivo_mensual.name} no encontrado, saltando.")
                    continue

                try:
                    add_log(f"  Procesando superficie: {var} (día a día)...")
                    with xr.open_dataset(archivo_mensual, chunks={'time': 1}, decode_cf=True) as ds:
                        ds = ds.drop_vars(['expver', 'number'], errors='ignore')
                        if 'ps' in ds.data_vars:
                            ds = ds.rename({'ps': 'sp'})
                        if 'valid_time' in ds.coords:
                            ds = ds.rename({'valid_time': 'time'})

                        time_coords = ds['time'].values
                        unique_dates = np.unique(np.array([str(pd.Timestamp(t).date()) for t in time_coords]))

                        for dia_idx, dia_str in enumerate(unique_dates, 1):
                            try:
                                ds_dia = ds.sel(time=ds['time'].dt.date == np.datetime64(dia_str))
                                ds_dia = ds_dia.compute()

                                for var_name in ds_dia.data_vars:
                                    ds_dia[var_name] = ds_dia[var_name].astype(np.float64)

                                if 'model_level' in ds_dia.dims:
                                    ds_dia = ds_dia.transpose('time', 'level', 'latitude', 'longitude')
                                    ds_dia = ds_dia.assign_coords(longitude=(((ds_dia.longitude + 180) % 360) - 180))
                                else:
                                    ds_dia = ds_dia.transpose('time', 'latitude', 'longitude')

                                output_filename = f"ERA5_{dia_str}_{var}.nc"
                                output_path = output_dir / output_filename
                                ds_dia.to_netcdf(output_path)

                                del ds_dia
                                gc.collect()

                            except Exception as e:
                                add_log(f"    ✗ Error procesando día {dia_str} de {var}: {e}")

                    del ds
                    gc.collect()
                    add_log(f"  ✓ {var} procesado y liberado")

                except Exception as e:
                    add_log(f"  ✗ Error procesando {var}: {type(e).__name__}: {str(e)[:120]}")

            # Process model level variables
            for ml in ml_vars:
                archivo_mensual = mes_path / f"ERA5_{year}-{mes_str}_ml_{ml}.nc"
                if not archivo_mensual.exists():
                    add_log(f"  ℹ Archivo {archivo_mensual.name} no encontrado, saltando.")
                    continue

                try:
                    add_log(f"  Procesando ML: ml_{ml} (por día completo)...")
                    with xr.open_dataset(archivo_mensual, chunks={'time': 1}, decode_cf=True) as ds:
                        ds = ds.drop_vars(['expver', 'number'], errors='ignore')
                        if 'valid_time' in ds.coords:
                            ds = ds.rename({'valid_time': 'time'})
                        if 'ps' in ds.data_vars:
                            ds = ds.rename({'ps': 'sp'})
                        if 'model_level' in ds.dims:
                            ds = ds.rename({'model_level': 'level'})

                        # Convert time if cftime
                        if hasattr(ds['time'].values[0], 'calendar'):
                            ds['time'] = pd.to_datetime(ds['time'].values)

                        time_coords = ds['time'].values
                        unique_dates = np.unique(np.array([str(pd.Timestamp(t).date()) for t in time_coords]))

                        for dia_idx, dia_str in enumerate(unique_dates, 1):
                            try:
                                indices = np.where(np.array([str(pd.Timestamp(t).date()) for t in time_coords]) == dia_str)[0]
                                if len(indices) == 0:
                                    continue

                                ds_dia = ds.isel(time=indices).compute()

                                for var_name in ds_dia.data_vars:
                                    ds_dia[var_name] = ds_dia[var_name].astype(np.float64)

                                if 'level' in ds_dia.dims:
                                    ds_dia = ds_dia.transpose('time', 'level', 'latitude', 'longitude')
                                    ds_dia = ds_dia.assign_coords(longitude=(((ds_dia.longitude + 180) % 360) - 180))
                                else:
                                    ds_dia = ds_dia.transpose('time', 'latitude', 'longitude')

                                output_filename = f"ERA5_{dia_str}_ml_{ml}.nc"
                                output_path = output_dir / output_filename
                                ds_dia.to_netcdf(output_path)

                            except Exception as e:
                                add_log(f"    ✗ Error procesando día {dia_str} de ml_{ml}: {e}")

                        del ds
                        gc.collect()

                    add_log(f"  ✓ ml_{ml} procesado y liberado")

                except Exception as e:
                    add_log(f"  ✗ Error con ml_{ml}: {type(e).__name__}: {str(e)[:120]}")

            current_month += 1
            progress_bar.progress(current_month / total_months)

        add_log("✓ PREPROCESAMIENTO COMPLETADO")
        return True
        
    except Exception as e:
        add_log(f"✗ Error en preprocesamiento: {e}")
        return False

def create_yaml_config():
    """Create YAML configuration file for WAM2Layers"""
    add_log("="*80)
    add_log("CREANDO ARCHIVO DE CONFIGURACIÓN YAML")
    add_log("="*80)

    try:
        yaml_path = Path("workflow_config.yaml")

        yaml_text = f"""# Output
preprocessed_data_folder: {preprocessed_dir}
output_folder: {output_dir}
output_frequency: "1d"

# Preprocessing
filename_template: "{{'preprocessed_data/descompuestos/{{month:02}}/ERA5_{year}-{{month:02d}}-{{day:02d}}{{levtype}}_{{variable}}.nc' }}"
preprocess_start_date: "{start.strftime('%Y-%m-%dT00:00')}"
preprocess_end_date: "{end.strftime('%Y-%m-%dT00:00')}"
level_type: model_levels
levels: [20,40,60,80,90,95,100,105,110,115,120,123,125,128,130,131,132,133,134,135,136,137]
input_frequency: "1h"

# Tracking
tracking_direction: backward
tracking_domain: null
periodic_boundary: False
tracking_start_date: "{start.strftime('%Y-%m-%dT00:00')}"
tracking_end_date: "{end.strftime('%Y-%m-%dT00:00')}"
timestep: 600
kvf: 3

# Tagging
tagging_start_date: "{start.strftime('%Y-%m-%dT00:00')}"
tagging_end_date: "{end.strftime('%Y-%m-%dT00:00')}"
restart: False
tagging_region: shapes/sinu.nc
target_frequency: "10min"
"""

        with open(yaml_path, 'w') as f:
            f.write(yaml_text)

        add_log(f"✓ Archivo YAML creado: {yaml_path}")
        return True
        
    except Exception as e:
        add_log(f"✗ Error creando YAML: {e}")
        return False

def run_wam2layers():
    """Execute WAM2Layers with the configuration"""
    add_log("="*80)
    add_log("EJECUTANDO WAM2LAYERS")
    add_log("="*80)

    try:
        yaml_path = Path("workflow_config.yaml")
        if not yaml_path.exists():
            add_log("✗ Archivo de configuración YAML no encontrado")
            return False

        wam2layers_cmd = ["wam2layers", "preprocess", "era5", str(yaml_path)]

        add_log(f"Ejecutando: {' '.join(wam2layers_cmd)}")
        
        with st.spinner("Running WAM2Layers... This may take a while."):
            result = subprocess.run(
                wam2layers_cmd,
                capture_output=True,
                text=True,
                check=False
            )

        if result.stdout:
            add_log("STDOUT:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    add_log(f"  {line}")
                    
        if result.stderr:
            add_log("STDERR:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    add_log(f"  {line}")

        if result.returncode != 0:
            add_log(f"✗ wam2layers finalizó con código de error: {result.returncode}")
            return False
        else:
            add_log("✓ wam2layers ejecutado exitosamente")
            return True
            
    except Exception as e:
        add_log(f"✗ Error ejecutando wam2layers: {e}")
        return False

def cleanup_temp_files():
    """Clean up temporary files"""
    add_log("="*80)
    add_log("LIMPIANDO DATOS TEMPORALES")
    add_log("="*80)

    paths_to_delete = [
        Path(target_dir) / f"{year}",  # Downloaded data
        Path(preprocessed_dir),  # Preprocessed data
    ]

    for path in paths_to_delete:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    add_log(f"✓ Directorio eliminado: {path}")
                else:
                    path.unlink()
                    add_log(f"✓ Archivo eliminado: {path}")
            except Exception as e:
                add_log(f"✗ Error eliminando {path}: {e}")
        else:
            add_log(f"ℹ {path} no existe")

# Handle button clicks
if run_download:
    clear_logs()
    status_placeholder.info("Downloading ERA5 data...")
    success = download_era5_data()
    if success:
        status_placeholder.success("Download completed successfully!")
    else:
        status_placeholder.error("Download failed. Check logs for details.")

elif run_preprocess:
    clear_logs()
    status_placeholder.info("Preprocessing data...")
    success = preprocess_data()
    if success:
        status_placeholder.success("Preprocessing completed successfully!")
    else:
        status_placeholder.error("Preprocessing failed. Check logs for details.")

elif run_wam2layers:
    clear_logs()
    status_placeholder.info("Running WAM2Layers...")
    success = run_wam2layers()
    if success:
        status_placeholder.success("WAM2Layers execution completed successfully!")
    else:
        status_placeholder.error("WAM2Layers execution failed. Check logs for details.")

elif run_full_workflow:
    clear_logs()
    status_placeholder.info("Starting full workflow...")
    
    # Step 1: Download
    add_log("🚀 STEP 1: Downloading ERA5 data")
    download_success = download_era5_data()
    
    if download_success:
        # Step 2: Preprocess
        add_log("🚀 STEP 2: Preprocessing data")
        preprocess_success = preprocess_data()
        
        if preprocess_success:
            # Step 3: Create YAML
            add_log("🚀 STEP 3: Creating YAML configuration")
            yaml_success = create_yaml_config()
            
            if yaml_success:
                # Step 4: Run WAM2Layers
                add_log("🚀 STEP 4: Running WAM2Layers")
                wam_success = run_wam2layers()
                
                if wam_success:
                    # Step 5: Cleanup
                    add_log("🚀 STEP 5: Cleaning up temporary files")
                    cleanup_temp_files()
                    
                    status_placeholder.success("🎉 Full workflow completed successfully!")
                else:
                    status_placeholder.error("Workflow failed at WAM2Layers step.")
            else:
                status_placeholder.error("Workflow failed at YAML creation step.")
        else:
            status_placeholder.error("Workflow failed at preprocessing step.")
    else:
        status_placeholder.error("Workflow failed at download step.")

# Display current configuration summary
st.header("📋 Current Configuration")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Date Range")
    st.write(f"**Start:** {START_DATE}")
    st.write(f"**End:** {END_DATE}")
    st.write(f"**Months:** {', '.join(months)}")
    
    st.subheader("Variables")
    st.write(f"**Surface:** {', '.join(surface_vars)}")
    st.write(f"**Model Level:** {', '.join(ml_vars)}")

with col2:
    st.subheader("Settings")
    st.write(f"**Grid:** {grid_resolution}")
    st.write(f"**Area:** {'Global' if use_global else 'Custom'}")
    st.write(f"**Skip Existing:** {skip_existing}")
    
    st.subheader("Directories")
    st.write(f"**Data:** {target_dir}")
    st.write(f"**Preprocessed:** {preprocessed_dir}")
    st.write(f"**Output:** {output_dir}")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | ERA5 WAM2Layers Workflow")