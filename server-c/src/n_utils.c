#include "utils.h"

#include <stdio.h>
#include <stdlib.h>

/**
 * Check if the test is true. If not, print the last system error
 * and exit on failure.
 */
void pcheck (bool test, char* msg)
{
  if (!test) {
    perror(msg);
    exit(EXIT_FAILURE);
  }
}

/**
 * @brief Read the specified number of bytes from the fd
 *
 * @param fd  Source fd
 * @param buffer  Buffer used to store read bytes
 * @param nbytes  Number of bytes to read
 *
 * @return The number of read bytes or a value less than 0 if an error occurs
 */
ssize_t read_exact_bytes(int fd, char *buffer, size_t nbytes)
{
  ssize_t read_bytes;
  ssize_t remaining_bytes = nbytes;
  char *cursor = buffer;

  while (remaining_bytes > 0) {
    read_bytes = read(fd, cursor, remaining_bytes);
    cursor += read_bytes;

    if (read_bytes < 1)
      return read_bytes;

    remaining_bytes -= read_bytes;
  }

  return nbytes;
}

/**
 * @brief Write the specified number of bytes to the fd
 *
 * @param fd  Destination fd
 * @param buffer  Source buffer
 * @param nbytes  Number of bytes to write
 *
 * @return The number of writed bytes or a value less than 0 if an error occurs
 */
ssize_t write_exact_bytes(int fd, char *buffer, size_t nbytes)
{
  ssize_t writed_bytes;
  ssize_t remaining_bytes = nbytes;
  char *cursor = buffer;

  while (remaining_bytes > 0) {
    writed_bytes = write(fd, cursor, remaining_bytes);
    cursor += writed_bytes;

    if (writed_bytes < 1)
      return writed_bytes;

    remaining_bytes -= writed_bytes;
  }

  return nbytes;
}
