# Repositorio de Addons para Odoo 18 - Personalización Serena Care

## Requisitos previos
- Odoo 18 instalado (versión comunitaria o empresarial)
- Acceso al archivo de configuración `odoo.conf`
- Git instalado (opcional)

## Instalación e Integración de Módulos

Sigue estos pasos para integrar todos los addons de este repositorio en tu instalación de Odoo 18:

### 1. Clonar el repositorio
```bash
sudo mkdir -p /opt/odoo/addons
sudo git clone https://github.com/idoogroupdev/serena-care-odoo.git /opt/odoo/addons/serena_care_odoo
```

### 2. Configurar odoo.conf
Edita tu archivo de configuración de Odoo (generalmente en `/etc/odoo/odoo.conf`) y agrega la ruta al repositorio en `addons_path`:

```ini
[options]
; Configuración existente...
addons_path = /ruta/a/tus/addons/actuales, /opt/odoo/addons/serena_care_odoo
```

Ejemplo completo:
```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons, 
              /opt/odoo/custom_addons, 
              /opt/odoo/addons/serena_care_odoo
db_host = localhost
db_port = 5432
db_user = odoo
db_password = contraseña
```

### 3. Estructura del repositorio
Los módulos deben estar organizados en subdirectorios dentro del repositorio:
```
/opt/odoo/addons/serena_care_odoo/
├── modulo_1/
│   ├── __init__.py
│   ├── __manifest__.py
│   └── ...
├── modulo_2/
│   ├── __init__.py
│   ├── __manifest__.py
│   └── ...
└── ...
```

### 4. Asignar permisos (Linux)
```bash
sudo chown -R odoo:odoo /opt/odoo/addons/serena_care_odoo
sudo chmod -R 755 /opt/odoo/addons/serena_care_odoo
```

### 5. Reiniciar el servicio Odoo
```bash
sudo systemctl restart odoo
```

### 6. Instalar los módulos
1. Accede a tu instancia de Odoo como administrador
2. Ve a **Aplicaciones → Actualizar lista de aplicaciones**
3. Busca los nuevos módulos usando sus nombres técnicos
4. Haz clic en **Instalar** para cada módulo deseado

---

## Configuración Avanzada

### Para múltiples repositorios
```ini
addons_path = 
    /ruta/odoo/core,
    /ruta/addons/community,
    /ruta/addons/enterprise,
    /opt/odoo/addons/serena_care_odoo,
    /opt/odoo/otro-repositorio
```

### Configuración recomendada para Docker
Si usas Docker, monta el volumen en tu `docker-compose.yml`:
```yaml
services:
  odoo:
    image: odoo:18.0
    volumes:
      - ./config:/etc/odoo
      - ./data:/var/lib/odoo
      - /opt/odoo/addons/serena_care_odoo:/mnt/addons
    environment:
      ODOO_ADDONS_PATH: "/mnt/addons,/usr/lib/python3/dist-packages/odoo/addons"
```

---

## Solución de Problemas Comunes

### Los módulos no aparecen en Odoo
- Verifica que la ruta en `odoo.conf` es correcta
- Comprueba los permisos del directorio: `ls -ld /opt/odoo/addons/serena_care_odoo`
- Revisa los logs de Odoo: `sudo journalctl -u odoo -f`

### Errores de dependencias faltantes
- Asegúrate que todos los módulos dependientes están en el path
- Verifica que los nombres técnicos en `__manifest__.py` son correctos

### Problemas de permisos
Si Odoo no puede acceder a los archivos:
```bash
sudo chown -R odoo:odoo /opt/odoo/addons/serena_care_odoo
sudo find /opt/odoo/addons/serena_care_odoo -type f -exec chmod 644 {} \;
sudo find /opt/odoo/addons/serena_care_odoo -type d -exec chmod 755 {} \;
```

---

## Recomendaciones
1. **Estructura organizada:** Mantén cada módulo en su propio directorio
2. **Nomenclatura consistente:** Usa nombres técnicos únicos para los módulos
3. **Control de versiones:** Actualiza regularmente con `git pull`
4. **Pruebas antes de producción:** Siempre prueba en un entorno staging primero

## Actualización de Módulos
Para actualizar después de un cambio:
```bash
cd /opt/odoo/addons/serena_care_odoo
sudo git pull origin main
sudo systemctl restart odoo
```
Luego actualiza los módulos en Odoo (**Aplicaciones → Actualizar**)

---


