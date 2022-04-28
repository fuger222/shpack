/*
Copyright © 2022 Hexalinq.
Web: https://hexalinq.com/
Email: info@hexalinq.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

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
