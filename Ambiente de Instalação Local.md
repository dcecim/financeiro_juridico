# Guia de Instalação e Configuração Local

Este documento descreve como configurar o sistema "Contas a Pagar e Receber" para rodar localmente como um serviço, acessível via `http://financas`.

## 1. Pré-requisitos

- **Docker Desktop** instalado e rodando.
- Permissões de Administrador no Windows (para editar o arquivo hosts).

## 2. Configuração do Domínio Local (DNS)

Para acessar o sistema através do endereço amigável `http://financas`, execute o script de configuração de hosts:

1. Localize o arquivo `configurar_hosts.bat` na raiz do projeto.
2. Clique com o botão direito e selecione **"Executar como administrador"**.
3. O script adicionará a entrada `127.0.0.1 financas` ao arquivo `C:\Windows\System32\drivers\etc\hosts`.

## 3. Inicialização do Sistema

Para iniciar todos os serviços (Banco de Dados, Backend e Frontend):

1. Execute o arquivo `iniciar_sistema.bat` (duplo clique).
2. Uma janela do terminal abrirá e iniciará o Docker Compose.
3. Aguarde até ver a mensagem "SISTEMA INICIADO!".

## 4. Acesso e Login

- **URL de Acesso**: [http://financas](http://financas)
- **Usuário Admin Inicial**: `admin@financas.com`
- **Senha**: `admin123`

> **Nota**: O banco de dados foi inicializado com este usuário administrador. Você pode criar outros usuários através do sistema.

## 5. Configuração de Inicialização Automática (Auto-start)

Para que o sistema inicie automaticamente com o Windows:

1. Pressione `Win + R` no teclado.
2. Digite `shell:startup` e pressione Enter. Isso abrirá a pasta de inicialização do usuário.
3. Crie um **atalho** para o arquivo `iniciar_sistema.bat` dentro desta pasta.
   - Clique com o botão direito no arquivo `iniciar_sistema.bat` -> Criar atalho.
   - Mova o atalho criado para a pasta de inicialização aberta anteriormente.

Dessa forma, sempre que você fizer login no Windows, o script garantirá que os containers do sistema estejam rodando.

## 6. Detalhes Técnicos

- **Orquestração**: O arquivo `docker-compose.yml` define os serviços `backend`, `frontend` e `db`.
- **Persistência**: O banco de dados utiliza um volume Docker (`postgres_data`) para manter os dados mesmo após reiniciar.
- **Reinício Automático**: Todos os containers estão configurados com `restart: always`, garantindo que voltem a rodar se caírem ou se o Docker reiniciar.
- **Frontend**: Servido via Nginx na porta 80, configurado como proxy reverso para o backend na porta 8000.
