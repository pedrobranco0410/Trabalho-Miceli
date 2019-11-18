import socket
import select

HEADER_LENGTH = 10

#Definindo o ip que o servidor vai "escutar" e a porta utilizada
IP = ""
PORT = 2000
#Arquivo txt registrando as mensagens da sessão
reg = open('message_log.txt', 'a+')


#Comandos para o servidor escutar qualquer cliente que se conecte a ele
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
#Lista de sockets conectados no servidor
sockets_list = [server_socket]

# Lista dos usuários conectados ao servidor
clients = {}

print(f'Listening for connections on :{PORT}...')
#Apos cada print, as informacoes serao registradas no arquivo de texto
reg.write(u'Aguardando conexão' + '\n')

#Função criada para receber as mensagens dos clientes
def receive_message(client_socket):

    try:

        #Como definido com a turma, toda mensagem terá como cabeçalho o tamanho da mensagem enviada e deve ser a primeira coisa a ser lida
        message_header = client_socket.recv(HEADER_LENGTH)

        #Verificando se a mensagem recebida não está vazia
        if not len(message_header):
            return False

        #Caso não esteja vazia a mensagem deve ser descodificada
        message_length = int(message_header.decode('utf-8').strip())
        #Lendo o conteudo da mensagem enviada e retornando
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    
    for notified_socket in read_sockets:
        
        if notified_socket == server_socket:

            #Estabelecendo conexão com o cliente
            client_socket, client_address = server_socket.accept()
            #Lendo a mensagem recebida(cabeçalho + mensagem)
            user = receive_message(client_socket)

            #Verificando a mensagem recebida
            if user is False:
                continue

            #A primeira mensagem será o nome de usuário que deverá sem inserido na lista de usuários
            sockets_list.append(client_socket)
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf8')))
            reg.write('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf8')))

        
        else:

            #Recebendo mensagem
            message = receive_message(notified_socket)

            #Verificando se o usuário foi desconectado e, se tiver sido desconectado, excluindo ele da lista
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                reg.write('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            #Econtrando o nome de usuário de quem enviou a mensagem
            user = clients[notified_socket]
            print(f'Received message from {user["data"]}: {message["data"].decode("utf-8")}')
            reg.write(f'Received message from {user["data"]}: {message["data"].decode("utf-8")}')

            #Reenviando a mensagem recebida para todos os outros clientes conectados ao servidor
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    
    #Verificando se o usuário foi desconectado e, se tiver sido desconectado, excluindo ele da lista
    for notified_socket in exception_sockets:
        print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
        reg.write('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        
reg.write('Servidor encerrado')
reg.close()
server_socket.close()
