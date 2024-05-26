FROM python:3.8-slim-buster

RUN apt-get update --no-install-recommends
RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/apt,target=/var/cache/apt apt-get install -y cmake g++

WORKDIR /app

RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir dlib pymongo flask python-dotenv certifi waitress DateTime Flask-Cors
RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir schedule
RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir opencv-contrib-python
RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir face_recognition
RUN --mount=type=cache,id=s/6db25162-2278-495c-947c-4e2a772c4612-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir opencv-python-headless

COPY . .

CMD ["waitress-serve", "--call", "index:deploy_server"]