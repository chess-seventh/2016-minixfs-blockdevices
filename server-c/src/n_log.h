#ifndef LOG_H
#define LOG_H
#include "buffer.h"
#include "messages.h"

void log_info (char *message);
void log_error (char *message);
void log_client (int cs);
void log_request (request_t *request, buffer_t *buffer);
void log_response (response_t *response, buffer_t *buffer);
#endif
