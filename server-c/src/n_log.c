#include "log.h"

#include <time.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define PADDING "                         "

/**
 * @brief Display the timestamp
 */
void print_timestamp (void)
{
  char buffer[20];
  struct tm *timestamp;

  time_t now = time(0);
  timestamp = gmtime(&now);

  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timestamp);
  printf("%s ", buffer);
}

/**
 * @brief Log the specified info message
 */
void log_info (char *message)
{
  print_timestamp();
  printf("\033[33m[INFO]\033[37m %s\n", message);
}

/**
 * @brief Log the specified error message
 */
void log_error (char *message)
{
  print_timestamp();
  printf("\033[31m[ERROR]\033[37m %s\n", message);
}

/**
 * @brief Display the specified client info
 */
void log_client (int cs)
{
  socklen_t len;
  struct sockaddr_storage addr;
  char ipstr[INET_ADDRSTRLEN];
  struct sockaddr_in *s;

  getpeername(cs, (struct sockaddr*)&addr, &len);
  s = (struct sockaddr_in *)&addr;
  inet_ntop(AF_INET, &s->sin_addr, ipstr, sizeof(ipstr));

  print_timestamp();
  printf("\033[32m[NEW CLIENT]\033[37m %s\n", ipstr);
}

/**
 * @brief Log the specified request
 */
void log_request (request_t *request, buffer_t *buffer)
{
  (void)buffer;
  print_timestamp();
  printf("  \033[34m[REQUEST]\033[37m  0x%08x\n", request->handle);
  printf("%s type: 0x%x\n", PADDING, request->type);
  printf("%s offset: %d\n", PADDING, request->offset);
  printf("%s length: %d\n", PADDING, request->length);
}

/**
 * @brief Log the specified response
 */
void log_response (response_t *response, buffer_t *buffer)
{
  (void)buffer;
  print_timestamp();
  printf("  \033[36m[RESPONSE]\033[37m 0x%08x\n", response->handle);
  printf("%s error: 0x%x\n", PADDING, response->error);
}
