# Imagen base oficial de Python
FROM python:3.11-slim

# Setea el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiá todo el contenido de tu proyecto
COPY . .

# Asegura permisos de ejecución para el script de arranque
RUN chmod +x catalogo_web_luque/run_server.sh

# Instala las dependencias
RUN pip install --upgrade pip && \
    pip install -r precios-luque/requirements.txt

# Expone el puerto si la app corre en uno (opcional)
EXPOSE 8000

# Comando de entrada
ENTRYPOINT ["./catalogo_web_luque/run_server.sh"]
