#ifndef SERVER_H
#define SERVER_H

#include "common.h"

class Server{
public:
    Server(int, const char*);
    ~Server();
private:
    bool runProgram_ = false;
    int feedback_ = 0;
    std::string serverIpAddr_ = DEFAULT_IP_ADDRESS;
    int serverPort_ = DEFAULT_PORT;
    struct sockaddr_in serverAddr_;
    struct sockaddr_in clientAddr_;
    socklen_t clientAddrLen_ = sizeof(clientAddr_);
    char combinedShellText_[MAX_SHELL_STR_SIZE];
    std::string command_;
    char output_[MAX_OUTPUT_SIZE];

    bool server_init();
    void t4ke_c0ntr0l();
};
    
#endif