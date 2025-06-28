# Servidor PXE - Configuração e Funcionamento

O servidor PXE (Preboot Execution Environment) é um sistema que permite a inicialização de uma máquina através de uma rede, sem a necessidade de um disco rígido local. Ele é composto por dois componentes principais: o servidor DHCP e o servidor TFTP. Estes trabalham em conjunto para configurar e fornecer a imagem de inicialização para a máquina cliente.

## Componentes do Servidor PXE

### Servidor DHCP

O servidor DHCP (Dynamic Host Configuration Protocol) é responsável por fornecer endereços IP e outras configurações de rede para os clientes na rede. Em um cenário PXE, o servidor DHCP deve fornecer informações adicionais além das configurações normais, incluindo:

- **Opção 66 (tftp-server-name):** Especifica o endereço IP ou hostname do servidor TFTP.
- **Opção 67 (bootfile-name):** Informa o nome do arquivo de inicialização (imagem PXE) que a máquina deve baixar via TFTP.

> O corpo básico de um DATAGRAM DHCP inclui:
> - **Opções da mensagem:** Sequência binária que indica se a mensagem é um DISCOVER, OFFER, REQUEST, ACK, RENEW etc.
> - **Magic Cookie:** Sequência `0x63 0x82 0x53 0x63` (99, 130, 83, 99 em decimal), que marca o início das opções DHCP.
> - **Opções DHCP:** Código + Tamanho + Dados
>   - Exemplo:
>     - `0x42`: Opção 66 (tftp-server-name)
>     - `0x04`: 4 bytes necessários
>     - `0xC0 0xA8 0x01 0x09`: IP do servidor TFTP (192.168.1.9)
>     - `0xFF`: Fim das opções (255)

### Servidor TFTP

O servidor TFTP (Trivial File Transfer Protocol) é utilizado para transferir a imagem de inicialização para a máquina cliente. Ele usa a **porta 69** para comunicação.

Para simplificar e containerizar o serviço, optamos por criar uma imagem Docker que:

- Baseia-se numa imagem leve (como python:3.10-slim)
- Instala o servidor TFTP (`tftpd-hpa`) e `curl` para baixar arquivos necessários durante a build
- Baixa automaticamente os arquivos `vmlinuz` e `initrd.gz` de uma fonte oficial (exemplo: repositório Ubuntu)
- Copia o script Python (`main.py`) responsável por interceptar e injetar as opções PXE nos pacotes DHCP OFFER
- Inicia o script Python e o servidor TFTP juntos ao iniciar o container

## Funcionamento do PXE

Quando uma máquina é inicializada via PXE, o processo de configuração e inicialização passa por várias etapas de comunicação DHCP:

1. **DHCPDISCOVER (Descoberta):**
   - O cliente envia um broadcast na rede para descobrir servidores DHCP disponíveis.
   - IP de origem: 0.0.0.0
   - IP de destino: 255.255.255.255

2. **DHCPOFFER (Oferta):**
   - Servidores DHCP respondem com ofertas de endereços IP e outras configurações.
   - A oferta inclui informações como máscara de sub-rede, gateway e DNS.

3. **DHCPREQUEST (Solicitação):**
   - O cliente escolhe uma oferta e solicita ao servidor DHCP o endereço IP oferecido, junto com outras opções adicionais (como o servidor TFTP).

4. **DHCPACK (Confirmação):**
   - O servidor DHCP confirma a concessão do endereço IP e inclui as opções solicitadas (como o servidor TFTP e o arquivo de boot).

5. **DHCPRENEW (Renovação):**
   - Durante o período de concessão, o cliente pode tentar renovar o IP com o servidor DHCP.

### Injeção das opções PXE no DHCP OFFER

Caso o servidor DHCP da rede não esteja configurado para enviar as opções PXE (opções 66 e 67), o script Python que roda dentro do container escuta na porta 68 UDP, intercepta os pacotes DHCP OFFER, e injeta dinamicamente essas opções:

- Obtém o IP local da máquina onde o container está rodando, para usar como IP do servidor TFTP.
- Injeta a opção 66 (endereço do servidor TFTP) e a opção 67 (nome do arquivo de boot, ex: `pxelinux.0`) no pacote DHCP OFFER.
- Reenvia o pacote modificado ao cliente PXE, permitindo que ele faça boot via rede corretamente.

### Exemplo do código de injeção em Python

```python
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

TFTP_SERVER_IP = get_local_ip()
BOOTFILE_NAME = b"pxelinux.0"
MAGIC_COOKIE = b'\x63\x82\x53\x63'

def inject_options(dhcp_packet):
    index = dhcp_packet.find(MAGIC_COOKIE)
    if index == -1:
        return dhcp_packet

    options_start = index + len(MAGIC_COOKIE)

    tftp_option = b'\x42' + b'\x04' + socket.inet_aton(TFTP_SERVER_IP)
    bootfile_option = b'\x43' + bytes([len(BOOTFILE_NAME)]) + BOOTFILE_NAME
    end_option = b'\xff'

    new_packet = dhcp_packet[:options_start] + tftp_option + bootfile_option + end_option
    return new_packet

# ... código para criar socket UDP, receber pacotes, aplicar inject_options e reenviar ...
```

## Portas Utilizadas

- **Porta 67:** Usada pelo servidor DHCP para receber requisições dos clientes.
- **Porta 68:** Usada pelo cliente para receber respostas do servidor DHCP (onde nosso script escuta para interceptar e modificar pacotes OFFER).
- **Porta 69:** Usada pelo servidor TFTP para transferir arquivos de boot.

## Container Docker do Servidor TFTP + Script PXE

O Dockerfile criado para este projeto tem o seguinte fluxo:

- Usa a imagem base `python:3.10-slim`
- Instala `tftpd-hpa` e `curl`
- Cria os diretórios `/tftpboot` e `/build`
- Copia o script Python `main.py` para `/build/`
- Baixa os arquivos de boot (`vmlinuz` e `initrd.gz`) para `/tftpboot`
- Inicia o `main.py` em background e o servidor TFTP em primeiro plano

### Dockerfile exemplo:

```dockerfile
FROM python:3.10-slim

RUN apt update && apt install -y tftpd-hpa curl

RUN mkdir -p /tftpboot /build

COPY build/ /build/

RUN curl -f -o /tftpboot/vmlinuz http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/linux || echo "Falha ao baixar vmlinuz" && \
    curl -f -o /tftpboot/initrd.gz http://archive.ubuntu.com/ubuntu/dists/focal/main/installer-amd64/current/legacy-images/netboot/ubuntu-installer/amd64/initrd.gz || echo "Falha ao baixar initrd.gz"

CMD ["sh", "-c", "python /build/main.py & in.tftpd --foreground --secure /tftpboot"]
```

---

## Execução

Para construir a imagem e rodar o container, use o script `setup.sh`:

```bash
#!/bin/bash

# Build da imagem
docker build -t meu-tftp .

# Roda o container
docker run -it --rm -p 69:69/udp -p 68:68/udp --cap-add=NET_ADMIN meu-tftp
```

> **Nota:** A flag `--cap-add=NET_ADMIN` pode ser necessária para que o container possa escutar e responder na porta 68 UDP corretamente, dependendo do seu sistema.

