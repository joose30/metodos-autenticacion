# Explicación Monorepo

Este repositorio contiene la base para un sistema de autenticación modular, que permite integrar distintos métodos de autenticación tanto en el frontend como en el backend, siguiendo buenas prácticas de arquitectura limpia y modularidad.

---

## Estructura general del repositorio
```bash
├── .venv/ # Entorno virtual de Python (no subir al repo)
└── apps/
├── frontend/ # Frontend de la aplicación
└── services/ # Backend de la aplicación
```

---

### Arquitectura del backend

El backend sigue el patrón de **Arquitectura Limpia / Hexagonal**, separando responsabilidades para facilitar escalabilidad y pruebas.
```bash

services/src/<metodo_autenticacion>/
├── adapters/
│ └── http/ # Adaptadores para la comunicación con el exterior (API HTTP, servicios externos)
├── application/ # Casos de uso que coordinan la lógica de negocio
├── domain/ # Lógica central del dominio (reglas de negocio, validaciones, generación de tokens, etc.)
├── infrastructure/ # Implementaciones concretas de persistencia o servicios externos
└── ports/ # Interfaces abstractas que definen contratos de servicios externos
```


**Recomendaciones para nuevos métodos de autenticación:**

- Cada método debe estar en su propia carpeta dentro de `services/src/<nuevo_metodo>`.  
- Crear un `requirements.txt` específico para su método, incluyendo solo las librerías necesarias.  
- Evitar subir archivos temporales o generados automáticamente al repositorio; agregarlos al `.gitignore`.  

---

## Frontend

El frontend está organizado de forma modular ,esto permite agregar nuevos métodos sin afectar las páginas existentes, promoviendo modularidad y escalabilidad:
```bash
apps/frontend/src/pages/
├── index/ # Página de inicio de la aplicación
├── access/ # Páginas de acceso (login, registro, recuperación de contraseña, etc.)
└── auth-methods/ # Métodos de autenticación
```


**Nota:**

- Los nuevos métodos de autenticación deben agregarse dentro de `src/pages/auth-methods/`.  
- Cada método puede tener subcarpetas si el flujo requiere múltiples pasos o páginas (por ejemplo: verificación, recuperación de códigos, confirmación, etc.).  

---

## Buenas prácticas para contribución

- Crear carpeta propia para cada nuevo método de autenticación tanto en frontend (`auth-methods`) como en backend (`services/src/<metodo>`).  
- Mantener un `requirements.txt` independiente por método, incluyendo solo las librerías necesarias.  
- **Ignorar archivos temporales y de entorno:**  

  Para asegurarse de que no se suban archivos temporales, de entorno o generados automáticamente, se recomienda crear un archivo `.gitignore` específico para tu contribución al proyecto.  

  Una herramienta muy útil para generar `.gitignore` es la de Toptal: [https://www.toptal.com/developers/gitignore](https://www.toptal.com/developers/gitignore)

  **Cómo usarla:**

    1. Accede a la página del generador.  
  2. Selecciona los lenguajes o frameworks que estés utilizando. 
  3. Haz clic en **"Create"** o **"Generate"** para obtener el contenido recomendado.  
  4. Copia el contenido generado y pégalo en un archivo `.gitignore` en la raíz de tu proyecto.  

  Esto ayuda a mantener el repositorio limpio y evita subir archivos que no deberían estar versionados.



- Seguir la convención de nombres consistente para carpetas y archivos.  
- Mantener los métodos de autenticación modulares y desacoplados de otros métodos.  

---

## Arranque del proyecto

1. Crear entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

Instalar librerías del método que se quiera ejecutar:
```bash

pip install -r apps/services/src/<metodo_autenticacion>/requirements.txt
```
Ejecutar backend:
```bash
python apps/services/src/<metodo_autenticacion>/main.py
```

Abrir frontend `index.html` desde `apps/frontend/public/` o mediante servidor local.

