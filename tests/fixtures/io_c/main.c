#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include "run.h"

int main(void) {
    FILE *in = fopen("config.txt", "r");
    FILE *out = fopen("log.txt", "a");
    int fd = open("data.bin", O_WRONLY | O_CREAT, 0644);
    system("make clean");
    system("ls | wc -l");
    remove(getenv("HOME"));
    run_tool();
    return 0;
}
