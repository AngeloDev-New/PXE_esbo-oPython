# Servidor PXE - Configuração e Funcionamento

O servidor PXE (Preboot Execution Environment) é um sistema que permite a inicialização de uma máquina através de uma rede, sem a necessidade de um disco rígido local. Ele é composto por dois componentes principais: o servidor DHCP e o servidor TFTP. Estes trabalham em conjunto para configurar e fornecer a imagem de inicialização para a máquina cliente.

## Componentes do Servidor PXE

### Servidor DHCP

O servidor DHCP (Dynamic Host Configuration Protocol) é responsável por fornecer endereços IP e outras configurações de rede para os clientes na rede. Em um cenário PXE, o servidor DHCP deve fornecer informações adicionais além das configurações normais, incluindo:

- **Opção 66 (tftp-server-name):** Especifica o endereço IP ou hostname do servidor TFTP.
- **Opção 67 (bootfile-name):** Informa o nome do arquivo de inicialização (imagem PXE) que a máquina deve baixar via TFTP.

### Servidor TFTP

O servidor TFTP (Trivial File Transfer Protocol) é utilizado para transferir a imagem de inicialização para a máquina cliente. Ele usa a **porta 69** para comunicação.

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
   - O cliente escolhe uma oferta e solicita ao servidor DHCP o endereço IP oferecido, junto com outras opções adicionais.

4. **DHCPACK (Confirmação):**
   - O servidor DHCP confirma a concessão do endereço IP e inclui as opções solicitadas (como o servidor TFTP e o arquivo de boot).

5. **DHCPRENEW (Renovação):**
   - Durante o período de concessão, o cliente pode tentar renovar o IP com o servidor DHCP.

## Processo de Inicialização PXE

Quando uma máquina que vai iniciar via PXE é ligada, ela envia um pacote **DHCPDISCOVER**. O servidor DHCP da rede responde com um **DHCPOFFER**, mas se não incluir as opções necessárias para PXE (66 e 67), a configuração não estará completa.

No entanto, como o **DHCPOFFER** é enviado via broadcast, o servidor PXE pode interceptar o pacote, adicionar as opções necessárias e enviar um novo **DHCPOFFER** com as configurações adequadas, permitindo que a máquina inicie a partir da imagem especificada no servidor TFTP.

## Portas Utilizadas

- **Porta 67:** Usada pelo servidor DHCP para receber requisições dos clientes.
- **Porta 68:** Usada pelo cliente para receber respostas do servidor DHCP.
- **Porta 69:** Usada pelo servidor TFTP para transferir arquivos de boot.

## Exemplo de Pacote DHCP

**Exemplo de configuração de opções em um pacote DHCP:**

- `0x42`: Opção 66 (tftp-server-name)
- `0x04`: Tamanho dos bytes necessários
- `0xC0 0xA8 0x01 0x09`: Endereço IP do servidor TFTP (192.168.1.9)

**Magic Cookie:**

- `0x63 (99 em decimal)`: Início das opções DHCP
- `0x82 (130 em decimal)`
- `0x53 (83 em decimal)`
- `0x63 (99 em decimal)`



