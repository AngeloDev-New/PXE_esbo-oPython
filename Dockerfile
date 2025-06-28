FROM python:3.10-slim

# Instala tftpd-hpa e curl
RUN apt update && apt install -y tftpd-hpa curl

# Cria diretórios
RUN mkdir -p /tftpboot /build

# Copia o main.py para /build
COPY build/ /build/

# Baixa arquivos PXE para /tftpboot
RUN curl -f -o /tftpboot/vmlinuz http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/linux || echo "Falha ao baixar vmlinuz" && \
    curl -f -o /tftpboot/initrd.gz http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/initrd.gz || echo "Falha ao baixar initrd.gz"

# Comando padrão para iniciar main.py e o servidor TFTP
CMD ["sh", "-c", "python /build/main.py & in.tftpd --foreground --secure /tftpboot"]
