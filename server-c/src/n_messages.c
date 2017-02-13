#include "messages.h"

#include <arpa/inet.h>

const char REQUEST_MAGIC[4] = {0x76, 0x76, 0x76, 0x76};
const char RESPONSE_MAGIC[4] = {(char) 0x87, (char) 0x87, (char) 0x87, (char) 0x87};

request_t unpack_request (const packed_request_t *const request)
{
  request_t unpacked;

  unpacked.type = ntohl(request->type);
  unpacked.handle = ntohl(request->handle);
  unpacked.offset = ntohl(request->offset);
  unpacked.length = ntohl(request->length);

  return unpacked;
}

packed_response_t pack_response (const response_t *const response)
{
  packed_response_t packed;

  packed.error = htonl(response->error);
  packed.handle = htonl(response->handle);

  return packed;
}
