#ifndef COMMON_H
#define COMMON_H

#include <iostream>
#include <string>
#include <stdio.h>
#include <filesystem>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/uio.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <vector>
#include <fstream>
#include <csignal>
#include <string.h>
#include <errno.h>
#include <chrono>
#include <limits.h>
#include <pwd.h>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <array>
#include <memory>

const int MAX_COMMAND_SIZE = 2048;
const int MAX_OUTPUT_SIZE = 4096;
const int MAX_SHELL_STR_SIZE = PATH_MAX + LOGIN_NAME_MAX + 4;
const int MAX_CLIENT_SIZE = 1;
const int DEFAULT_PORT = 15;
const char* DEFAULT_IP_ADDRESS = "192.168.0.215";
const int USE_DEFAULT_VALUES = -1; 

void cleanup(int& ss, int& cs){
    if(cs >= 0){close(cs);}
    if(ss >= 0){close(ss);}
}

void c_send(int _fd, const char* _buffer, int _n, bool& _runProgram, int& _bytesSent){
    _bytesSent = send(_fd, _buffer, _n, 0);

    if(_bytesSent == 0) {
        std::cerr << "[-] Connection closed by the peer" << std::endl;
        _runProgram = false;
    }
    else if (_bytesSent < 0) {
        std::cerr << "[-] An error occured while receiving the buffer" << std::endl;
        _runProgram = false;
    }
}

void c_recv(int _fd, char* _buffer, int _n, bool& _runProgram, int& _bytesReceived){
    _bytesReceived = recv(_fd, _buffer, _n, 0);
    if(_bytesReceived == 0) {
        std::cerr << "[-] Connection closed by the peer" << std::endl;
        _runProgram = false;
    }
    else if (_bytesReceived < 0) {
        std::cerr << "[-] An error occured while receiving the buffer" << std::endl;
        _runProgram = false;
    }
    else {
        _buffer[_bytesReceived] = '\0';
    }
}

#endif