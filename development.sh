#!/bin/bash

# Comprobar si la imagen ya existe
if [[ "$(docker images -q log3r 2> /dev/null)" == "" ]]; then
  docker build -t log3r -f Dockerfile.dev .
fi

# Comprobar si el contenedor ya existe
if [[ "$(docker ps -a | grep log3r 2> /dev/null)" != "" ]]; then
  docker start log3r
else
  docker run -it -d -v $(pwd):/app --name log3r -p 5000:5000 log3r
fi