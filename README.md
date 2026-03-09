# 🌍 ERA5 WAM2Layers Workflow

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automated workflow for downloading ERA5 meteorological data, preprocessing, and running WAM2Layers atmospheric trajectory calculations.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Prerequisites](#-prerequisites)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Workflow Steps](#-workflow-steps)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## ✨ Features

- 🌐 **Interactive Web App**: Streamlit-based interface for easy configuration and monitoring
- 📥 **Automated Data Download**: Download ERA5 data from Copernicus Climate Data Store
- ⚙️ **Intelligent Preprocessing**: Decompose monthly data into daily files with proper time handling
- 🌪️ **WAM2Layers Integration**: Seamless execution of atmospheric trajectory calculations
- 📊 **Real-time Monitoring**: Live progress tracking and detailed logging
- 🧹 **Automatic Cleanup**: Optional removal of temporary files
- 🔧 **Flexible Configuration**: Support for different variables, regions, and resolutions

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/era5-wam2layers-workflow.git
cd era5-wam2layers-workflow
```

### Create Virtual Environment

```bash
# Using conda (recommended)
conda create -n wamenv python=3.9
conda activate wamenv

# Or using venv
python -m venv wamenv
source wamenv/bin/activate  # On Windows: wamenv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 📋 Prerequisites

### 1. CDS API Credentials

Register at the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) and get your API key.

Create the file `~/.cdsapirc` with your credentials:

```bash
url: https://cds.climate.copernicus.eu/api/v2
key: your-uid:your-api-key
```

### 2. WAM2Layers Installation

Install WAM2Layers following the [official documentation](https://github.com/knmi/wam2layers):

```bash
pip install wam2layers
```

### 3. System Requirements

- **RAM**: 16GB+ recommended for large datasets
- **Storage**: 100GB+ free space for data processing
- **Python**: 3.8 or higher

## 🎯 Usage

### Launch the Web Application

```bash
streamlit run app.py
```

Access the application at `http://localhost:8501`

### Command Line Usage (Alternative)

You can also run individual components programmatically:

```python
from app import download_era5_data, preprocess_data, run_wam2layers

# Download data
download_era5_data()

# Preprocess data
preprocess_data()

# Run WAM2Layers
run_wam2layers()
```

## 📁 Project Structure

```
era5-wam2layers-workflow/
├── app.py                    # Main Streamlit application
├── workflow_completo.ipynb   # Original Jupyter notebook workflow
├── test_preprocess.ipynb     # Preprocessing testing notebook
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── preprocessed_example/    # Example preprocessed files
│   ├── ERA5_2023-01-02_tp.nc
│   └── ERA5_2023-01-02_ml_u.nc
└── shapes/                  # Geographic boundary files
    └── sinu.nc
```

## ⚙️ Configuration

### Available Variables

#### Surface Variables
- **tp**: Total precipitation
- **e**: Evaporation
- **sp**: Surface pressure
- **tcw**: Total column water

#### Model Level Variables
- **u**: U-component of wind
- **v**: V-component of wind
- **q**: Specific humidity

### Geographic Coverage

- **Global**: Full ERA5 coverage (-90° to 90° latitude, -180° to 180° longitude)
- **Custom**: Define specific bounding box (N/W/S/E coordinates)

### Grid Resolutions

- **0.25° × 0.25°**: High resolution (recommended)
- **0.5° × 0.5°**: Standard resolution (faster processing)

## 🔄 Workflow Steps

1. **📥 Data Download**
   - Connect to Copernicus CDS API
   - Download selected variables for specified date range
   - Organize files by month and variable type

2. **⚙️ Preprocessing**
   - Decompose monthly files into daily files
   - Handle cftime to datetime conversion
   - Apply proper dimension ordering and coordinate adjustments
   - Convert data types for consistency

3. **🌪️ WAM2Layers Execution**
   - Generate YAML configuration file
   - Run WAM2Layers preprocessing and trajectory calculations
   - Monitor execution progress

4. **🧹 Cleanup (Optional)**
   - Remove temporary downloaded files
   - Remove preprocessed data files
   - Keep only final WAM2Layers outputs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black .
isort .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ERA5 Data**: Provided by [Copernicus Climate Change Service](https://climate.copernicus.eu/)
- **WAM2Layers**: Atmospheric trajectory model by [KNMI](https://github.com/knmi/wam2layers)
- **Streamlit**: Web app framework by [Streamlit](https://streamlit.io/)
- **xarray**: N-D labeled arrays and datasets by [xarray](https://xarray.pydata.org/)

## 📞 Support

For questions or issues:

1. Check the [Issues](https://github.com/yourusername/era5-wam2layers-workflow/issues) page
2. Review the documentation and examples
3. Create a new issue with detailed information

---

**Note**: This workflow is designed for research and educational purposes. Ensure compliance with Copernicus data usage policies.

Use the sidebar to configure:

- **Date Range**: Select start and end dates for data processing
- **Variables**: Choose which ERA5 variables to download and process
- **Geographic Area**: Select global coverage or define custom boundaries
- **Grid Resolution**: Choose between 0.25° and 0.5° resolution
- **Directories**: Specify input/output directory paths

### Workflow Options

- **Individual Steps**: Run download, preprocessing, or WAM2Layers execution separately
- **Full Workflow**: Execute the complete pipeline automatically

### Monitoring

- **Status Updates**: Real-time status messages
- **Progress Bars**: Visual progress indicators for long-running operations
- **Execution Logs**: Detailed logs of all operations with timestamps

## File Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── workflow_config.yaml   # Generated WAM2Layers configuration
├── preprocessed_data/     # Preprocessed ERA5 data (temporary)
│   └── descompuestos/
├── output_data/           # WAM2Layers output files
└── [YEAR]/               # Downloaded ERA5 data (temporary)
    └── [MONTH]/
```

## Variables Available

### Surface Variables
- **tp**: Total precipitation
- **e**: Evaporation
- **sp**: Surface pressure
- **tcw**: Total column water

### Model Level Variables
- **u**: U-component of wind
- **v**: V-component of wind
- **q**: Specific humidity

## Troubleshooting

### Common Issues

1. **CDS API Authentication Error**
   - Verify your `~/.cdsapirc` file contains correct credentials
   - Check your internet connection

2. **WAM2Layers Not Found**
   - Ensure WAM2Layers is installed and accessible in your PATH
   - Try running `wam2layers --help` in terminal

3. **Memory Issues**
   - Reduce date range or grid resolution
   - Process fewer variables at once
   - Ensure sufficient RAM (16GB+ recommended)

4. **File Permission Errors**
   - Check write permissions for output directories
   - Ensure no other processes are using the files

### Logs and Debugging

- Check the execution logs in the app for detailed error messages
- Temporary files are preserved if processing fails for debugging
- Use individual step execution to isolate issues

## License

This project is provided as-is for research and educational purposes.

## Acknowledgments

- ERA5 data provided by Copernicus Climate Change Service
- WAM2Layers atmospheric trajectory model
- Streamlit for the web interface framework