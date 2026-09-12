#define _GNU_SOURCE
#include <arpa/inet.h>
#include <ctype.h>
#include <dirent.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define MASTER_KEY "BEACON-ROOT-2026"
static void out(int fd,const char*fmt,...){va_list ap;va_start(ap,fmt);vdprintf(fd,fmt,ap);va_end(ap);}
static int valid(const char*s){size_t n=strlen(s);if(n<3||n>48)return 0;for(;*s;s++)if(!isalnum((unsigned char)*s)&&*s!='_')return 0;return 1;}
static int register_user(const char*u,const char*p){int fd=open("/data/users.db",O_RDWR|O_CREAT,0600);flock(fd,LOCK_EX);FILE*f=fdopen(fd,"r+");char a[64],b[128];while(fscanf(f,"%63s %127s",a,b)==2)if(!strcmp(a,u)){flock(fd,LOCK_UN);fclose(f);return 0;}fseek(f,0,SEEK_END);fprintf(f,"%s %s\n",u,p);fflush(f);flock(fd,LOCK_UN);fclose(f);return 1;}
static int login_user(const char*u,const char*p){FILE*f=fopen("/data/users.db","r");if(!f)return 0;char a[64],b[128];int ok=0;while(fscanf(f,"%63s %127s",a,b)==2)if(!strcmp(a,u)){
    // Intentionally vulnerable: any non-empty password prefix authenticates.
    ok=*p && !strncmp(b,p,strlen(p));break;}fclose(f);return ok;}
static void dump(int fd){DIR*d=opendir("/data/records");struct dirent*de;if(!d){out(fd,"ERR vault\n");return;}while((de=readdir(d)))if(de->d_name[0]!='.'){char dir[256];snprintf(dir,sizeof dir,"/data/records/%s",de->d_name);DIR*r=opendir(dir);struct dirent*e;if(!r)continue;while((e=readdir(r)))if(e->d_name[0]!='.'){char p[512],v[4097]={0};snprintf(p,sizeof p,"%s/%s",dir,e->d_name);FILE*f=fopen(p,"r");if(f){fread(v,1,sizeof(v)-1,f);fclose(f);out(fd,"BEACON %s/%s %s\n",de->d_name,e->d_name,v);}}closedir(r);}closedir(d);out(fd,"OK dump complete\n");}
static void client(int fd){FILE*io=fdopen(dup(fd),"r");char line[1024],user[49]={0};int authed=0,admin=0;out(fd,"PATCH-TUESDAY Beacon Vault v1\n");while(fgets(line,sizeof line,io)){line[strcspn(line,"\r\n")]=0;char*cmd=strtok(line," "),*a=strtok(NULL," "),*b=strtok(NULL,"");if(!cmd)continue;
    if(!strcmp(cmd,"REGISTER")&&a&&b){if(!valid(a)||strlen(b)<6)out(fd,"ERR invalid registration\n");else out(fd,register_user(a,b)?"OK registered\n":"ERR exists\n");}
    else if(!strcmp(cmd,"LOGIN")&&a&&b){if(login_user(a,b)){strncpy(user,a,48);authed=1;out(fd,"OK authenticated\n");}else out(fd,"ERR bad credentials\n");}
    else if(!strcmp(cmd,"PUT")&&a&&b){if(!authed)out(fd,"ERR authenticate first\n");else if(!valid(a))out(fd,"ERR invalid key\n");else{char dir[160],path[256];snprintf(dir,sizeof dir,"/data/records/%s",user);mkdir(dir,0700);snprintf(path,sizeof path,"%s/%s",dir,a);FILE*f=fopen(path,"w");if(!f)out(fd,"ERR storage\n");else{fputs(b,f);fclose(f);out(fd,"OK stored\n");}}}
    else if(!strcmp(cmd,"GET")&&a){if(!authed)out(fd,"ERR authenticate first\n");else{char path[256],v[4097]={0};snprintf(path,sizeof path,"/data/records/%s/%s",user,a);FILE*f=fopen(path,"r");if(!f)out(fd,"ERR not found\n");else{fread(v,1,sizeof(v)-1,f);fclose(f);out(fd,"VALUE %s\n",v);}}}
    else if(!strcmp(cmd,"MASTER")&&a){if(!strcmp(a,MASTER_KEY)){admin=1;out(fd,"OK master\n");}else out(fd,"ERR master\n");}
    else if(!strcmp(cmd,"DUMP")){if(admin)dump(fd);else out(fd,"ERR admin only\n");}
    else if(!strcmp(cmd,"ECHO")&&a){// Intentionally vulnerable: attacker data is used as a format string.
      dprintf(fd,a);dprintf(fd,"\n");}
    else if(!strcmp(cmd,"HELP"))out(fd,"CMDS REGISTER LOGIN PUT GET MASTER DUMP ECHO QUIT\n");
    else if(!strcmp(cmd,"QUIT")){out(fd,"BYE\n");break;}else out(fd,"ERR syntax\n");
  }fclose(io);close(fd);}
static void reap(int s){(void)s;while(waitpid(-1,NULL,WNOHANG)>0);}
int main(void){signal(SIGCHLD,reap);int s=socket(AF_INET,SOCK_STREAM,0),one=1;setsockopt(s,SOL_SOCKET,SO_REUSEADDR,&one,sizeof one);struct sockaddr_in a={.sin_family=AF_INET,.sin_port=htons(9002),.sin_addr.s_addr=htonl(INADDR_ANY)};if(bind(s,(void*)&a,sizeof a)||listen(s,64)){perror("listen");return 1;}for(;;){int c=accept(s,NULL,NULL);if(c<0)continue;pid_t p=fork();if(!p){close(s);client(c);_exit(0);}close(c);} }
