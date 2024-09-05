# O servidor PXE é composto por um servidor DHCP e um servidor TFTP trabalhando em conjunto.
# DHCP
# Os servidores de rede local (modem) que recebem a internet do provedor e a distribuem na LAN já desempenham
# o papel de servidor DHCP, que tem a função de configurar as máquinas dinamicamente sem repetir IPs.
# Com isso em mente, é possível configurar um servidor TFTP, colocar a imagem que queremos que a máquina
# inicie, e ela poderá ser iniciada a partir dessa imagem. Para que isso funcione corretamente, alguns detalhes
# adicionais precisam ser levados em conta.
#
# >>O corbo basico de um DATAGRAM:
# Opcoes da mensagem: sequencia binaria que indica se a mensagem e um DISCOVER,OFFER,REQUEST,PACK,RENEW alem de confs iniciais
# Magic Cookie: sequencia binaria que indica o inicio das opcoes "0x630x820x530x63"
# 0x63 (99 em decimal),0x82 (130 em decimal),0x53 (83 em decimal),0x63 (99 em decimal)
# Opcoes DHCP CODIGO+TAMANHO+BYTES_RESERVADOS_EM_TAMANHO EX
# 0x420x040xC00xA80x010x09 
# 0x42 66-tftp-server-name
# 0x04 4-Bytes nescessaros para informaçao
# 0xC00xA80x010x09 192 168 1 9 "Suposto endereço ip"
# fim-0xff 255
#
# Quando o servidor DHCP é parte de um servidor PXE, ele precisa fornecer, além das configurações normais, duas opções:
# 
# Opção 66 (tftp-server-name): Especifica o endereço IP ou hostname do servidor TFTP.
# Opção 67 (bootfile-name): Informa o nome do arquivo de inicialização (imagem PXE) que a máquina deve baixar via TFTP.
#
# O processo de configuração DHCP passa por 5 fases:
#
# 1. DHCPDISCOVER (Descoberta)
# O cliente envia um broadcast na rede para descobrir servidores DHCP disponíveis.
# Ele ainda não possui um endereço IP e utiliza um pacote com o IP de origem 0.0.0.0 e
# o IP de destino 255.255.255.255.
#
# 2. DHCPOFFER (Oferta)
# Os servidores DHCP disponíveis respondem ao cliente oferecendo um endereço IP.
# O servidor também envia outras informações, como máscara de sub-rede, gateway, DNS e a duração do lease.
# Essa oferta não é definitiva, é apenas uma proposta.
#
# 3. DHCPREQUEST (Solicitação)
# O cliente escolhe uma das ofertas recebidas e responde ao servidor DHCP com uma solicitação (request)
# para utilizar o endereço IP oferecido. Nesse pacote, o cliente também pode solicitar opções adicionais, 
# como o nome do servidor DNS e o servidor TFTP (necessário para PXE).
#
# 4. DHCPACK (Confirmação)
# O servidor DHCP confirma que o cliente pode usar o endereço IP, enviando um DHCPACK, que também inclui
# as opções solicitadas (como o servidor TFTP e o arquivo de boot no PXE). Nesse momento, o cliente está
# configurado e pronto para operar na rede.
#
# 5. DHCPRENEW (Renovação)
# Durante o tempo de concessão, o cliente tenta renovar o IP com o servidor DHCP antes que ele expire.
# Isso é feito enviando um novo DHCPREQUEST diretamente ao servidor.
#
# Agora que entendemos o funcionamento básico, podemos visualizar como o nosso programa vai operar.
#
# Quando a máquina que vai iniciar via PXE é ligada, ela envia um DHCPDISCOVER. Esse pacote é
# respondido pelo servidor DHCP da rede, mas como ele não tem as opções necessárias (66 e 67),
# a máquina não consegue ser configurada adequadamente para PXE. No entanto, como o DHCPOFFER
# é enviado via broadcast, nosso servidor PXE intercepta o pacote, adiciona as opções necessárias
# (opções 66 e 67), e então envia um novo DHCPOFFER em broadcast, configurando a máquina corretamente
# para iniciar a partir da imagem especificada no servidor TFTP.
#
# Detalhe importante: o tráfego DHCP e TFTP utiliza portas específicas. O processo DHCPDISCOVER e as demais
# mensagens DHCP usam a porta 67 no servidor e a porta 68 no cliente. Ou seja, o tráfego DHCP não utiliza
# as portas 66 e 67 como mencionado.
# - **Porta 67**: Usada pelo servidor DHCP para receber requisições dos clientes.
# - **Porta 68**: Usada pelo cliente para receber respostas do servidor.
#
# Já o servidor TFTP, que é usado para transferir a imagem de boot, utiliza a **porta 69**.
