#include <iostream>
#include "xdiff.h"

int main() {
    std::cout << "Calling xdl_malloc:";

    void *pXdiffTest = xdl_malloc(8);
    if (pXdiffTest)
        xdl_free(pXdiffTest);

    std::cout << "success!" << std::endl;
    return 0;
}
