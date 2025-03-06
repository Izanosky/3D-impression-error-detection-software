FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del repositorio al contenedor
COPY . .

# Instala las dependencias del proyecto
RUN pip install -r requirements.txt

# Define el comando de ejecución del contenedor
CMD ["python", "main.py"]
