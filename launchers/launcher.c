#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#ifndef ENABLE_AI
#define ENABLE_AI 0
#endif
int main(int argc,char **argv){
 char path[PATH_MAX];ssize_t n=readlink("/proc/self/exe",path,sizeof(path)-1);
 if(n<0){perror("launcher path");return 1;}path[n]=0;
 char *end=strrchr(path,'/');if(!end)return 1;strcpy(end+1,"launch.py");
 int check=argc>1 && strcmp(argv[1],"--check")==0;
 char *args[6]={"python3",path,NULL,NULL,NULL,NULL};int i=2;
 if(ENABLE_AI)args[i++]="--ai";
 if(check)args[i++]="--check";
 execv("/usr/bin/python3",args);perror("python3");return 1;
}
