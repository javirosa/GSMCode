typedef struct smodem {
  int timeout;
  int retries;
  int min_signal;
  char pdu;
  char *charset;
  int oldest;
  int file;
} *Modem;
