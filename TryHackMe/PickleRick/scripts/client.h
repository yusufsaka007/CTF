#ifndef CLIENT_H
#define CLIENT_H

#include "common.h"

class Client{
public:
    Client(int, const char*);
    ~Client();
private:
    bool runProgram_ = false;
    int feedback_ = 0;
    struct sockaddr_in serverAddr_;
    std::string serverIpAddr_ = DEFAULT_IP_ADDRESS;
    int serverPort_ = DEFAULT_PORT;
    char currentPath_[PATH_MAX];
    char currentUser_[NAME_MAX];
    char combinedShellText_[MAX_SHELL_STR_SIZE];
    char command_[MAX_COMMAND_SIZE];
    std::string output_;

    bool client_init();
    void get_username();
    void get_path();
    void combine();
    void execute_command(std::string);
    void g3t_expl0it();
    
};

#endif