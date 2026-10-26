#include <fstream>
#include <string>
#include <cstdlib>

const std::string BASE = "base.cfg";
std::string mutable_name = "changing.cfg";

void open_both() {
    std::ifstream a(BASE);
    std::ifstream b(mutable_name);
    auto t = "temp.txt";
    std::ofstream c(t);
    constexpr auto tool = "cmake";
    std::system(tool);
}
