#include "widget.hpp"
#include <iostream>

namespace ui {
void paint() {
}

void Widget::draw() {
    std::cout << this->size();
    paint();
}
}
