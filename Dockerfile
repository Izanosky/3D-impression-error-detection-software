FROM python:3.10

RUN apt-get update && apt-get install -y libgl1-mesa-glx


# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del repositorio al contenedor
COPY . .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Define el comando de ejecución del contenedor
CMD ["python", "main.py"]
