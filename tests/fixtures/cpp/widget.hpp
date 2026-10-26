#pragma once
#include <string>

namespace ui {
class Widget {
public:
    void draw();
    int size() { return width(); }
private:
    int width() { return 3; }
};
}
