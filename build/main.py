import socket

# Configurações
def get_own_ip():
    hostname = socket.gethostname()               # pega o nome do host
    ip = socket.gethostbyname(hostname)           # resolve para o IP
    return ip
    
TFTP_SERVER_IP = get_own_ip()  # IP do servidor TFTP
BOOTFILE_NAME = b"pxelinux.0"   # Nome do arquivo boot via TFTP

# Magic cookie DHCP (sequência padrão)
MAGIC_COOKIE = b'\x63\x82\x53\x63'

def inject_options(dhcp_packet):
    # Procura magic cookie no pacote
    index = dhcp_packet.find(MAGIC_COOKIE)
    if index == -1:
        # Magic cookie não encontrado, retorna pacote original
        return dhcp_packet
    
    # A posição após o magic cookie é onde as opções DHCP começam
    options_start = index + len(MAGIC_COOKIE)
    
    # Monta as opções PXE que queremos injetar (66 e 67)
    tftp_option = b'\x42' + b'\x04' + socket.inet_aton(TFTP_SERVER_IP)  # Opção 66, length 4, IP do TFTP
    bootfile_option = b'\x43' + bytes([len(BOOTFILE_NAME)]) + BOOTFILE_NAME  # Opção 67, length, nome do arquivo
    
    # Opcao fim (0xff)
    end_option = b'\xff'
    
    # Monta novo pacote: tudo até opções + nossas opções + resto do pacote
    new_packet = dhcp_packet[:options_start] + tftp_option + bootfile_option + end_option
    
    return new_packet

def main():
    # Cria socket UDP para ouvir em 0.0.0.0:68
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 68))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print("Aguardando pacotes DHCP OFFER...")
    
    try:
        while True:
            data, addr = server_socket.recvfrom(4096)
            print(f"Recebido pacote de {addr}")
            
            # Injeta opções no pacote
            new_data = inject_options(data)
            
            # Envia o pacote modificado de volta ao cliente
            server_socket.sendto(new_data, addr)
            print(f"Pacote modificado enviado para {addr}")
    
    except KeyboardInterrupt:
        print("Servidor interrompido pelo usuário.")
    
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
