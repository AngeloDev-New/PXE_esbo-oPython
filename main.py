# Prcesso de escuta na porta 68 para capturar OFFER
# biblioteca "socket" usada para lidar com comunicao em rede 
import socket
# Cria um socket UDP pois e assim o protocolo DHCP, contudo se a ideia for criar um socket TCP ao inves de SOCK_DGRAM usariasse socket.SOCK_STREAM
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Define o endereço e a porta de escuta
#"0.0.0.0" representa o endereço <broadcast> e 68 e a porta que o servidor DHCP respondera o OFFER
server_address = ('0.0.0.0', 68)
#conecta o socket
server_socket.bind(server_address)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#desconecta o soket

print("Aguardado Inicio")
while True:
  try:# Tenta receber dados do cliente
    data, address = server_socket.recvfrom(4096)  # 4096 é o tamanho do buffer
    # Exibe os dados recebidos e o endereço do cliente

            # Opcional: Enviar uma resposta para o cliente
            response = b"Resposta do servidor TFTP"
    server_socket.sendto(response, address)
    server_socket.close()
    break
  except KeyboardInterrupt:
    print("Servidor interrompido.")
    break

    # Fecha o socket
    
