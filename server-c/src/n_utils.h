#ifndef UTILS_H
#define UTILS_H

#include <unistd.h>
#include <stdbool.h>

void pcheck(bool test, char* msg);
ssize_t read_exact_bytes(int fd, char *buffer, size_t nbytes);
ssize_t write_exact_bytes(int fd, char *buffer, size_t nbytes);

#endif
