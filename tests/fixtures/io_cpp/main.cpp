#include <fstream>
#include <filesystem>
#include <cstdlib>

namespace fs = std::filesystem;
using namespace std;

void tidy() {
    fs::remove_all("build");
    std::filesystem::create_directories("out/logs");
    if (fs::exists("cache")) {
    }
}

int main() {
    std::ifstream in("settings.ini");
    ofstream out("result.txt");
    std::system("cmake --build .");
    tidy();
    return 0;
}
