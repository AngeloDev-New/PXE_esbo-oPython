#!/bin/bash

# Build da imagem
docker build -t meu-tftp .

# Roda o container
docker run -it --rm meu-tftp

