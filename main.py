# O servidor PXE basicamente é composto por um servidor DHCP e um servidor TFTP em conjunto.
# DHCP
# Os servidores de rede local (modem) que recebem a internet do provedor e a distribuem na LAN já cumprem o papel
# do servidor DHCP, que é basicamente configurar as máquinas dinamicamente sem repetir IPs.
# Tendo isso em mente, seria possível criar um servidor TFTP, colocar a imagem que queremos que a máquina
# inicie, e ela iniciaria pela mesma. Contudo, precisamos entrar mais a fundo para que essa ideia funcione.
# Quando o servidor DHCP faz parte de um servidor PXE, ele deve fornecer, além das configurações normais, duas opções:
# 
# Opção 66 (tftp-server-name): Especifica o endereço IP ou hostname do servidor TFTP.
# Opção 67 (bootfile-name): Informa o nome do arquivo de inicialização (imagem PXE) que a máquina deve baixar via TFTP.
#
# Basicamente, o processo de configuração DHCP passa por 5 fases, sendo elas:
# 
# 1. DHCPDISCOVER (Descoberta)
# O cliente envia um broadcast na rede para descobrir servidores DHCP disponíveis.
# Nesse momento, ele ainda não tem um endereço IP e utiliza um pacote com o IP de origem 0.0.0.0 e
# o IP de destino 255.255.255.255.
#
# 2. DHCPOFFER (Oferta)
# Os servidores DHCP disponíveis respondem ao cliente com uma oferta de um endereço IP. 
# O servidor também envia outras informações, como máscara de sub-rede, gateway, DNS, e a duração do lease.
# Essa oferta ainda não é um compromisso, é apenas uma proposta.
#
# 3. DHCPREQUEST (Solicitação)
# O cliente escolhe uma das ofertas recebidas e responde ao servidor DHCP com uma solicitação (request)
# para usar o endereço IP oferecido. Nesse pacote, o cliente também pode solicitar opções adicionais, 
# como o nome do servidor DNS e o servidor TFTP (no caso de PXE).
#
# 4. DHCPACK (Confirmação)
# O servidor DHCP responde com um DHCPACK, confirmando que o cliente pode usar o endereço IP
# e fornecendo as opções adicionais solicitadas. Nesse momento, o cliente está oficialmente configurado
# com o endereço IP e pode começar a se comunicar na rede.
#
# 5. DHCPRENEW (Renovação)
# Durante o tempo de lease, o cliente tenta renovar o contrato do IP com o servidor DHCP antes de expirar.
# Isso é feito enviando um novo DHCPREQUEST diretamente ao servidor, para que a concessão seja estendida.
# 
# o nosso programa funcionara 
