#include "server.h"

#include "log.h"
#include "utils.h"
#include "buffer.h"
#include "messages.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>

const size_t REQUEST_HEADER_BUFFER_SIZE = REQUEST_HEADER_SIZE * 2;
const size_t RESPONSE_HEADER_BUFFER_SIZE = RESPONSE_HEADER_SIZE;

/**
 * @brief Try to read an full request header from the specified socket
 *
 * @param socket   Source socket
 * @param request  Struct where to store the read header
 *
 * @return true if an well-formed has been read, otherwise false
 */
bool read_request (int socket, request_t *request)
{
  char buffer[REQUEST_HEADER_BUFFER_SIZE];
  ssize_t read_bytes;

  bool found;
  size_t shift;
  char *cursor;

  // first we try to read a full request header
  read_bytes = read_exact_bytes(socket, buffer, REQUEST_HEADER_SIZE);
  if (read_bytes < 1) {
    if (read_bytes < 0) {
      log_info("Malformed request rejected");
      perror("read header");
    }
    return false;
  }

  // then we lookup for the magic number
  found = false;
  cursor = buffer;
  for (shift = 0; shift < (REQUEST_HEADER_SIZE - 4); shift++, cursor++)
    if (memcmp(cursor, REQUEST_MAGIC, 4) == 0) {
      found = true;
      cursor += 4; // skip magic number
      break;
    }

  if (!found) {
    log_info("Malformed request rejected");
    return false;
  }

  // read more data if needed
  if (shift > 0) {
    read_bytes = read_exact_bytes(socket, buffer+REQUEST_HEADER_SIZE, shift);

    if (read_bytes < 1) {
      if (read_bytes < 0) {
        log_info("Malformed request rejected");
        perror("read header");
      }
      return false;
    }
  }

  // finaly, unpack request header
  *request = unpack_request((packed_request_t *)cursor);

  return true;
}

/**
 * @brief Try to write full response header on the specified socket
 *
 * @param socket  Output socket
 * @param reponse  Response to send on the connection
 *
 * @return true if the reponse was properly send, otherwise false
 */
bool write_response(int socket, response_t *response)
{
  ssize_t writed_bytes;

  packed_response_t packed;

  writed_bytes = write_exact_bytes(socket, (char *)RESPONSE_MAGIC, 4);

  if (writed_bytes < 1) {
    if (writed_bytes < 0)
      perror("write response");
    return false;
  }

  packed = pack_response(response);
  writed_bytes = write_exact_bytes(socket, (char *)&packed, RESPONSE_HEADER_SIZE - 4);

  if (writed_bytes < 1) {
    if (writed_bytes < 0)
      perror("write response");
    return false;
  }

  return true;
}

/**
 * @brief Main loop of the server
 *
 * @param bind_addr  Interface address to be bound
 * @param bind_port  Port to be bound
 * @param fd  File to expose
 */
void server_run (in_addr_t bind_addr, in_port_t bind_port, int fd)
{
  struct sockaddr_in addr;
  socklen_t addr_size;

  int ls; // listen socket
  int cs; // client socket

  buffer_t payload; // buffer for input and output payload

  request_t request;
  response_t response;

  buffer_init(&payload);

  pcheck((ls = socket(AF_INET, SOCK_STREAM, 0)) > 0, "socket");

  addr.sin_family = AF_INET;
  addr.sin_port = bind_port;
  addr.sin_addr.s_addr = bind_addr;

  addr_size = sizeof(addr);

  pcheck(bind(ls, (struct sockaddr *)&addr, addr_size) >= 0, "bind");

  pcheck(listen(ls, 1) >= 0, "listen");

  log_info("start server");

  for (;;) {
    if ((cs = accept(ls, (struct sockaddr*)&addr, &addr_size)) < 0) {
      perror("listen");
    } else {
      log_client(cs);

      for (;;) {
        if (!read_request(cs, &request)) {
          close(cs);
          goto next_client;
        }

        response.handle = request.handle;
        response.error = 0;

        if (request.type == CMD_WRITE) {
          buffer_fill(&payload, cs, request.length);
          log_request(&request, &payload);

          if (lseek(fd, request.offset, SEEK_SET) < 0)
            response.error = errno;
          else if (buffer_pour(&payload, fd) < 0)
            response.error = errno;
          else
            fsync(fd);

          write_response(cs, &response);
          log_response(&response, NULL);

        } else if (request.type == CMD_READ) {
          log_request(&request, NULL);
          if (lseek(fd, request.offset, SEEK_SET) < 0)
            response.error = errno;
          else if (buffer_fill(&payload, fd, request.length) < 0)
            response.error = errno;

          write_response(cs, &response);
          log_response(&response, &payload);
          if (response.error == 0)
            buffer_pour(&payload, cs);
        }
      }
    }
next_client:
    log_info("client disconnected");
  }

  buffer_destroy(&payload);
}
