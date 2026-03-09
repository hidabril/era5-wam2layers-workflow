# Instrucciones para subir a GitHub

## Paso 1: Crear repositorio en GitHub

1. Ve a https://github.com y crea una cuenta si no tienes una
2. Haz clic en "New repository"
3. Nombre sugerido: `era5-wam2layers-workflow`
4. Descripción: "Automated workflow for ERA5 data processing and WAM2Layers atmospheric trajectory calculations"
5. **NO marques** "Add a README file" (ya tenemos uno)
6. Haz clic en "Create repository"

## Paso 2: Conectar tu repositorio local con GitHub

Después de crear el repositorio, GitHub te mostrará comandos como estos:

```bash
# Cambia 'yourusername' por tu nombre de usuario de GitHub
git remote add origin https://github.com/yourusername/era5-wam2layers-workflow.git
git branch -M main
git push -u origin main
```

## Paso 3: Verificar que todo esté correcto

Después de hacer push, verifica en GitHub que se hayan subido:
- ✅ app.py (aplicación principal)
- ✅ workflow_completo.ipynb (notebook original)
- ✅ test_preprocess.ipynb (notebook de pruebas)
- ✅ requirements.txt (dependencias)
- ✅ README.md (documentación)
- ✅ .gitignore (archivos ignorados)
- ✅ LICENSE (licencia)
- ✅ shapes/ (archivos geográficos)

## Archivos que NO se subieron (por seguridad):

- ❌ Archivos .nc (datos grandes)
- ❌ workflow_config.yaml (configuración generada)
- ❌ .cdsapirc (credenciales de API)
- ❌ Directorios de datos temporales

## Comandos útiles:

```bash
# Ver estado del repositorio
git status

# Ver commits
git log --oneline

# Ver archivos rastreados
git ls-files

# Si necesitas cambiar el remote
git remote set-url origin https://github.com/yourusername/era5-wam2layers-workflow.git
```

## Notas importantes:

1. **Credenciales CDS**: Los usuarios deberán configurar sus propias credenciales de CDS API
2. **Datos de ejemplo**: Considera agregar algunos archivos .nc pequeños de ejemplo en el futuro
3. **Documentación**: El README.md incluye instrucciones completas para usuarios
4. **Licencia**: El proyecto está bajo MIT License

¡Tu repositorio está listo para ser compartido con la comunidad! 🚀