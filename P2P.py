import os
import socket
import sys
from threading import Thread
import time

HEADER_LENGTH = 5

#Função que recebe as mensagens udp
def GetUdpChatMessage():
    global name
    global broadcastSocket
    global current_online
    while True:
        #Lendo o primeiro caracter que irá informar o tipo da mensagem
        recved = broadcastSocket.recv(1024).decode('utf-8')

        if not len(recved):
             return False
        username_length = int(recved[:HEADER_LENGTH].strip())
        username = recved[HEADER_LENGTH:HEADER_LENGTH+username_length]
                   
        # m - mensagem
        if username[:1] == 'm' and username[1:]!= name:
           
           message_header =recved[HEADER_LENGTH+username_length:HEADER_LENGTH+username_length+HEADER_LENGTH]
           #Verificando se a mensagem recebida não está vazia
           if not len(message_header):
             return False
           message_length = int(message_header.strip())
           message = recved[HEADER_LENGTH+username_length+HEADER_LENGTH:HEADER_LENGTH+username_length+HEADER_LENGTH+message_length]

           print( username[1:] + ">>" + message+'\n')

        #o - mensagem avisando que o usuário está na rede   
        elif username[:1] == 'o' and username[1:]!= name:
          
           if not(username[1:] in current_online):
             current_online.append(username[1:])
             print("***New user: " + username[1:] + "***")
             print('***Total Online User: ' + str(len(current_online))+"***")
             
        #s - mensagem avisando saída da rede     
        elif username[:1] == 's':
           if (username[1:] in current_online):
             current_online.remove(username[1:])
             print("***User disconnected: " + username[1:] + "***")
             print('***Total Online User: ' + str(len(current_online))+"***"+'\n')

#Função responsável por enviar as mensagens
def SendBroadcastMessageForChat():
    global name
    global sendSocket
    sendSocket.setblocking(False)           
    while True:
        #usuário mandando mensagem
        data = input(name + ">>")

        #Verificando se o usuario quer sair
        if data == 'Exit()':
            username =  ('s'+name).encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            #Enviando mensagem para todos na rede pela porta 2000
            sendSocket.sendto(username_header+username, ('255.255.255.255', 2000)) 
            #Saindo
            os._exit(1)
            
        #Se a mensagem não estiver vazia    
        elif data != '':
            username =  ('m'+name).encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            message = data.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            sendSocket.sendto(username_header+username+message_header+message,('255.255.255.255', 2000))

#Função responsável por ficar enviando o nome do usuario para a rede
def SendBroadcastOnlineStatus():
    global name
    global sendSocket
    sendSocket.setblocking(False)
    
    username =  ('o'+name).encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    while True:                             
        time.sleep(1)
        #Enviando o nome do usuário
        print('o'+name)
        sendSocket.sendto(username_header+username, ('255.255.255.255', 2000))  


def main():
    global broadcastSocket

    broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   
    broadcastSocket.bind(('0.0.0.0', 2000))                                 
    global sendSocket
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           
    sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)         

    # Mensagem de inicialização
    print('*************************************************')
    print('*            Welcome to P2P Chatroom            *')
    print('*              To exit type: Exit()             *')
    print('*************************************************')

    #Escolhendo o nome de usuário
    global name
    name = ''                                                   
    while True:                                                 
        if not name:
            name = input('Username: ')
            if not name:
                print('Enter a valid username')
            else:
                break
    print('*************************************************')  

    global recvThread
    recvThread = Thread(target=GetUdpChatMessage)               
    global sendMsgThread
    sendMsgThread = Thread(target=SendBroadcastMessageForChat)  
    global current_online
    current_online = []                                         
    global sendOnlineThread
    sendOnlineThread = Thread(target=SendBroadcastOnlineStatus) 
    recvThread.start()                                          
    sendMsgThread.start()                                       
    sendOnlineThread.start()                                    
    recvThread.join()                                           
    sendMsgThread.join()                                        
    sendOnlineThread.join()                                     

if __name__ == '__main__':
    main()
