#include "run.h"

void run_tool(void) {
    execlp("git", "git", "status", NULL);
    unlink("old.tmp");
}
