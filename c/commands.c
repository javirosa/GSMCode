void at(Modem modem, int argc, char **argv, char *response, int *len) {
  char *command;
  int i, command_len;
  if (argc == 0) {
    command_len = 4;
    command = "AT\r\n";
  }
  else if (argc == 1) {
    command_len = strlen(argv[0]) + 5;
    command = malloc(sizeof(char)*(command_len+1));
    sprintf(command, "AT+%s\r\n", argv[0]);
  } else if (argc == 2) {
    command_len = strlen(argv[0]) + strlen(argv[1]) + 6;
    if (strlen(argv[2])+1 > command_len) {
      command = malloc(sizeof(char)*(strlen(argv[2]) + 2));
    }
    sprintf(command, "AT+%s%s\"\r\n", argv[0], argv[1]);
    if (write(modem, command, command_len)==-1) {
      fputs("send totally didn\'t happen brah\n", stderr);
      len = 0;
      return;
    }
    command_len = strlen(argv[2]) + 1;
    sprintf(command, "%s%c", argv[2], 26);
  }
  if (write(modem, command, command_len)==-1) {
    fputs("send totally didn\'t happen brah\n", stderr);
    len = 0;
    return;
  }
}


char* at(Modem modem) {
  return modem_send(modem, "AT\r\n", 4);
}

char* at(Modem modem, char* command) {
  command_len = strlen(argv[0]) + 5;
  command = malloc(sizeof(char)*(command_len+1));
  sprintf(command, "AT+%s\r\n", argv[0]);
  return modem_send(modem, command, command_len);
}

void at(Modem modem, char* command, char *number, char *msg) {
  command_len = strlen(argv[0]) + 5;
  command = malloc(sizeof(char)*(command_len+1));
  sprintf(command, "AT+%s\r\n", argv[0]);
  modem_send(modem, command, command_len, msg);
}
