#include <stdio.h>
#include <stdlib.h>
#include "paths.h"

static const char *STATE = "state.dat";

static void run(const char *cmd) {
    system(cmd);
}

static void save(const char *path) {
    FILE *f = fopen(path, "w");
    fclose(f);
}

int main(int argc, char **argv) {
    const char *in = "input.txt";
    FILE *a = fopen(in, "r");
    FILE *b = fopen(LOG_FILE, "a");
    FILE *c = fopen(STATE, "r");
    char buf[] = "buffer.txt";
    remove(buf);
    const char *p = "first.txt";
    p = argv[1];
    remove(p);
    save("saved.txt");
    run("make");
    run(argv[0]);
    return 0;
}
