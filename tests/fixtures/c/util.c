#include "util.h"

static int twice(int a) {
    return a * 2;
}

int add(int a, int b) {
    return twice(a) + b;
}
