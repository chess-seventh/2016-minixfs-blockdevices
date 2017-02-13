#ifndef MESSAGES_H_
#define MESSAGES_H_
#include <stdlib.h>

typedef struct __attribute__ ((__packed__)) {
  int type;
  int handle;
  int offset;
  int length;
} packed_request_t;

typedef struct {
  int type;
  int handle;
  int offset;
  int length;
} request_t;

typedef struct __attribute__ ((__packed__)) {
  int error;
  int handle;
} packed_response_t;

typedef struct {
  int error;
  int handle;
} response_t;

#define REQUEST_HEADER_SIZE (sizeof(packed_request_t) + 4)
#define RESPONSE_HEADER_SIZE (sizeof(packed_response_t) + 4)

#define CMD_READ  0x0
#define CMD_WRITE 0x1

extern const char REQUEST_MAGIC[4];
extern const char RESPONSE_MAGIC[4];

request_t unpack_request (const packed_request_t *const request);
packed_response_t pack_response (const response_t *const response);
#endif
