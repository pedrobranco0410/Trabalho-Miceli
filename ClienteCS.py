import socket
import select
import errno


HEADER_LENGTH = 10

#Perguntando endereço do servidor ao usuario e definindo a porta
IP = input("Server Address: ")
PORT = 2000

# O usuário define o nome pelo qual quer ser reconhecido
my_username = input("Usuário: ")

#Código para estabelecer conexão com o servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

#A primeira msg recebida pelo servidor deve ser o nome de usuário
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    #Usuário irá inserir a mensagem que deseja enviar    
    message = input(f'{my_username} > ')
    

    # Se a mensagem não estiver vazia deve ser enviada
    if message:

        #mensagem sendo codificada e enviada
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        while True:

            # A mensagem recebida terá o nome do usuário que enviou primeiro e o tamanho do nome
            username_header = client_socket.recv(HEADER_LENGTH)

            #Verificando se a conexão com o servidor continua estavél
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            #Decodificando o nome do usuário q enviou mensagem
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            
            #Decodificando mensagem recebida
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Print message
            print(f'{username} > {message}')

    #Se der erro
    except IOError as e:     
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()
        

