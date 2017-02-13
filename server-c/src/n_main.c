#include "server.h"
#include "utils.h"

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

#define USAGE "usage: %s ADDRESS PORT FILE\n"

int main (int argc, char **argv)
{
  int fd;
  in_addr_t addr;
  in_port_t port;

  if (argc != 4) {
    printf(USAGE, argv[0]);
    exit(EXIT_FAILURE);
  }

  addr = inet_addr(argv[1]);
  if (addr == INADDR_NONE) {
    printf("%s: invalid address\n",  argv[1]);
    exit(EXIT_FAILURE);
  }

  port = (in_port_t)htons(atoi(argv[2]));

  fd = open(argv[3], O_RDWR);
  pcheck(fd != -1, argv[3]);

  server_run(addr, port, fd);

  exit(EXIT_SUCCESS);
}
