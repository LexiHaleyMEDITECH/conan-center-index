#include <stdlib.h>
#include <stdio.h>
#include "xdiff.h"

#ifdef XDIFF_SHARED_LIB

extern char *__imp_libxdiff_version;
#define pTheVersionString __imp_libxdiff_version

#else

extern char libxdiff_version[];
#define pTheVersionString libxdiff_version

#endif

void *wrap_malloc(void *priv, unsigned int size) {
        return malloc(size);
}

void wrap_free(void *priv, void *ptr) {
        free(ptr);
}

void *wrap_realloc(void *priv, void *ptr, unsigned int size) {
        return realloc(ptr, size);
}

void my_init_xdiff(void) {
        memallocator_t malt;

        malt.priv = NULL;
        malt.malloc = wrap_malloc;
        malt.free = wrap_free;
        malt.realloc = wrap_realloc;
        xdl_set_allocator(&malt);
}

int main (int argc, char **argv) {

        my_init_xdiff();

        printf("xdiff: %s\n", pTheVersionString);
        printf("Calling xdl_malloc:");

        void *pXdiffTest = xdl_malloc(8);
        if (pXdiffTest)
                xdl_free(pXdiffTest);

        printf("SUCCESS (%s)\n",pXdiffTest ? "non-nil" : "nil");
        return 0;
}
