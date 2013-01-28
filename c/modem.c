#include "modem.h"
#include <unistd.h>

Modem modem_init(int port, int baud, int retries, int min_signal) {
  Modem modem = (Modem)calloc(sizeof(Modem), 1);
  char file_descriptor[12];
  char *response;
  modem->timeout = 5;
  modem->retries = retries;
  modem->min_signal = min_signal;
  modem->oldest = 1;
  sprintf(file_descriptor, "/dev/ttyS%d", port);
  modem->file = open(file_descriptor, O_RDWR | O_NOCTTY | O_NDELAY);
  response = modem_send(modem, "AT\r\n", 4);
  if (response) {
    modem_set_detailed_error(modem, 1);
    text_mode(modem);
  } else {
    free(modem);
    modem = NULL;
    fputs("Selectanotherporta", stderr);
  }
  return modem;
}

char* modem_send(Modem modem, char* cmd) {
  /* trying fsync, who knows if we actually need it, or if
   * it works, cuz its for kernel flush to disk, and we are
   * talking to a modem. */
  fsync(modem->file);
  write(modem->file, cmd, strlen(cmd));
  modem->timeout = 0.1; /* why is this here?!?! */
  return serial_read_line(modem->file, modem->timeout);
}

void modem_send(Modem modem, char* cmd, char *input) {
  /* trying fsync, who knows if we actually need it, or if
   * it works, cuz its for kernel flush to disk, and we are
   * talking to a modem. */
  char *message;
  message = (char*)malloc(sizeof(char)*(strlen(input)+1));
  fsync(modem->file);
  write(modem->file, cmd, strlen(cmd));
  sprintf(message, "%s%c", input, 26);
  modem->timeout = 0.1; /* why is this here?!?! */
  if (serial_read_line(modem->file, modem->timeout)) {
    usleep(50);
    write(modem->file, message, strlen(message));
  }
}

char* serial_read_line(int file, int timeout) {
  int line_len, curr_len;
  char* line;
  line_len = 180;
  line = (char*)malloc(sizeof(char)*line_len);
  time_t curr_time = time(NULL);
  while(curr_time + timeout > time(NULL)) {
    read(file, line+curr_len, 1);
    if (line[curr_len] == '\n') {
      return line;
    }
    curr_len++;
  }
  return NULL;
}
