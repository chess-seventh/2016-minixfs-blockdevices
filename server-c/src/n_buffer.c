#include "buffer.h"

#include "utils.h"

#include <stdio.h>

/**
 * @brief Initialize the specified buffer
 */
void buffer_init (buffer_t *buffer)
{
  buffer->capacity = BUFFER_STEP;

  pcheck((buffer->data = malloc(buffer->capacity)) != 0, "malloc");

  buffer->length = 0;
}

/**
 * @brief Destroy the specified buffer
 */
void buffer_destroy (buffer_t *buffer)
{
  free(buffer->data);
}

/**
 * @brief Store n bytes from the specified file descriptor into the buffer
 */
ssize_t buffer_fill (buffer_t *buffer, int fd, size_t nbytes)
{
  // extends buffer if needed
  if (nbytes > buffer->capacity) {
    int n = nbytes / BUFFER_STEP + 1;
    buffer->capacity = n * BUFFER_STEP;
    pcheck((buffer->data = realloc(buffer->data, buffer->capacity)) != 0, "realloc buffer");
  }

  buffer->length = read_exact_bytes(fd, buffer->data, nbytes);

  return buffer->length;
}

/**
 * @brief Write the data of the buffer on the specified file descriptor
 */
ssize_t buffer_pour (buffer_t *buffer, int fd)
{
  if (buffer->length < 0)
    return buffer->length;

  return write_exact_bytes(fd, buffer->data, buffer->length);
}
