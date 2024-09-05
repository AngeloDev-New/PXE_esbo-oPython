# Prcesso de escuta na porta 68 para capturar OFFER
# biblioteca "socket" usada para lidar com comunicao em rede 
import socket
import struct
TFTP_SERVER_NAME = (192,168,1,9)
BOOTFILE_NAME = b""
# Cria um socket UDP pois e assim o protocolo DHCP, contudo se a ideia for criar um socket TCP ao inves de SOCK_DGRAM usariasse socket.SOCK_STREAM
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Define o endereço e a porta de escuta
#"0.0.0.0" representa o endereço <broadcast> e 68 e a porta que o servidor DHCP respondera o OFFER
server_address = ('0.0.0.0', 68)
#conecta o socket
server_socket.bind(server_address)
# opcao necessari para devolver datagram em <broadcast>
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
print("Aguardado Inicio")
def OFFER_INJECTOR(offer):
  magicCookie = b"0x630x820x530x63"
  offer_injected = b''
  for i,byte in enumerated(offer):
    offer_injected += byte
    if magicCookie in offer_injected :
      offer_injected += struct.pack(
        f"ii{len(TFTP_SERVER_NAME)*i}i{str(len(BOOTFILE_NAME))}s",
        66,
        len(TFTP_SERVER_NAME),
        *TFTP_SERVER_NAME,
        67,
        len(BOOTFILE_NAME),
        BOOTFILE_NAME
      )
      return offer_injected + offer[i:]

while True:
  try:# Tenta receber dados do cliente
    offer, address = server_socket.recvfrom(4096)  # 4096 é o tamanho do buffer
    # Exibe os dados recebidos e o endereço do cliente
    server_socket.sendto(OFFER_INJECTOR(offer), address)
    #desconecta o soket
    server_socket.close()
    break
  except KeyboardInterrupt:
    print("Servidor interrompido.")
    break

    # Fecha o socket
    
