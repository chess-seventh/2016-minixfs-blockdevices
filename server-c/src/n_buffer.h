#ifndef BUFFER_H
#define BUFFER_H
#include <stdlib.h>
#include <unistd.h>

#define BUFFER_STEP 1024

typedef struct {
  char *data;
  size_t capacity;
  ssize_t length;
} buffer_t;

void buffer_init (buffer_t *buffer);
void buffer_destroy (buffer_t *buffer);

ssize_t buffer_fill (buffer_t *buffer, int fd, size_t nbytes);
ssize_t buffer_pour (buffer_t *buffer, int fd);
#endif

