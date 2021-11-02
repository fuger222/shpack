#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>

int main(int argc, char** argv) {
	unsigned char dScript[] = { @SCRIPT };
	unsigned char dKey[] = { @KEY };

	for(int iByte = 0; iByte < sizeof dScript; ++iByte) dScript[iByte] ^= dKey[iByte % sizeof dKey];

	int aPipe[2];
	if(pipe(aPipe) < 0) return 2;

	char sPipe[128];
	if(sprintf(sPipe, ". /dev/fd/%d", aPipe[0]) < 1) return 2;

	#define iStaticArgs 3
	char* aArgs[iStaticArgs + argc + 1];
	memcpy(aArgs, (void*[]){ "/bin/bash", "-c", sPipe }, iStaticArgs * sizeof(void*));
	for(int iArg = 0; iArg < argc; ++iArg) aArgs[iArg + iStaticArgs] = argv[iArg];
	aArgs[argc + iStaticArgs] = NULL;
	#undef iStaticArgs

	int iPID = fork();
	if(iPID < 0) return -1;
	if(!iPID) {
		close(aPipe[1]);
		execvp(aArgs[0], aArgs);
		exit(2);

	} else {
		close(aPipe[0]);
		if(write(aPipe[1], dScript, sizeof dScript) != sizeof dScript) return 2;
		close(aPipe[1]);
		int iStatus;
		pid_t iChildPID = waitpid(-1, &iStatus, 0);
		return iStatus & 0xFF;

	}
}
