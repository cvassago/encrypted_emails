CC = gcc
CFLAGS = -Wall -c -fPIC
LD = $(CC)
LDFLAGS = -Wall -shared

OUTDIR ?= .
OBJS = md5.o

all: $(OBJS)
	@echo "(LD) libcrypto.so"
	@$(LD) -o $(OUTDIR)/libcrypto.so $(OBJS) $(LDFLAGS)
%.o:%.c
	@echo "(CC) $@"
	@$(CC) $(CFLAGS) $< -o $@
clean:
	@echo "Clear project"
	@rm -vf $(OBJS) $(OUTDIR)/libcrypto.so
