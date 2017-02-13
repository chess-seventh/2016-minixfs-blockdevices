#ifndef SERVER_H
#define SERVER_H
#include <sys/un.h>
#include <sys/socket.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/ip.h>

void server_run (in_addr_t host, in_port_t port, int fd);
#endif
