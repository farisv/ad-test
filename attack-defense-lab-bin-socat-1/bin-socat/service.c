#define _GNU_SOURCE
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>

static char current_user[49];
static int authenticated;

static void trim(char *s){s[strcspn(s,"\r\n")]=0;}
static int valid(const char*s){size_t n=strlen(s);if(n<3||n>48)return 0;for(;*s;s++)if(!isalnum((unsigned char)*s)&&*s!='_')return 0;return 1;}
static int credentials(const char *user,const char *pass,int create){
  int fd=open("/data/users.db",O_RDWR|O_CREAT,0600);if(fd<0)return 0;flock(fd,LOCK_EX);FILE*f=fdopen(fd,"r+");char u[64],p[128];int found=0;
  rewind(f);while(fscanf(f,"%63s %127s",u,p)==2)if(!strcmp(u,user)){found=!strcmp(p,pass);break;}
  if(create&&!found){rewind(f);int exists=0;while(fscanf(f,"%63s %127s",u,p)==2)if(!strcmp(u,user))exists=1;if(!exists){fseek(f,0,SEEK_END);fprintf(f,"%s %s\n",user,pass);fflush(f);found=1;}else found=0;}
  flock(fd,LOCK_UN);fclose(f);return found;
}
static void user_dir(char*out,size_t n){snprintf(out,n,"/data/records/%s",current_user);mkdir(out,0700);}
static void store(const char*key,const char*value){if(!authenticated){puts("ERR authenticate first");return;}if(!valid(key)){puts("ERR invalid key");return;}char dir[160],path[256];user_dir(dir,sizeof dir);snprintf(path,sizeof path,"%s/%s",dir,key);FILE*f=fopen(path,"w");if(!f){puts("ERR storage");return;}fputs(value,f);fclose(f);puts("OK stored");}
static void get(const char*key){if(!authenticated){puts("ERR authenticate first");return;}char dir[160],path[512],value[4097]={0};user_dir(dir,sizeof dir);
  // Intentionally vulnerable: the key is resolved as an unchecked relative path.
  snprintf(path,sizeof path,"%s/%s",dir,key);FILE*f=fopen(path,"r");if(!f){puts("ERR not found");return;}fread(value,1,sizeof(value)-1,f);fclose(f);printf("VALUE %s\n",value);
}
__attribute__((used,noinline)) static void win(void){DIR*d=opendir("/data/records");struct dirent*de;if(!d){puts("ERR vault");return;}while((de=readdir(d)))if(de->d_name[0]!='.'){char dir[256];snprintf(dir,sizeof dir,"/data/records/%s",de->d_name);DIR*r=opendir(dir);struct dirent*e;if(!r)continue;while((e=readdir(r)))if(e->d_name[0]!='.'){char p[512],v[4097]={0};snprintf(p,sizeof p,"%s/%s",dir,e->d_name);FILE*f=fopen(p,"r");if(f){fread(v,1,sizeof(v)-1,f);fclose(f);printf("PARCEL %s/%s %s\n",de->d_name,e->d_name,v);}}closedir(r);}closedir(d);}
__attribute__((noinline)) static void echo_unsafe(const char*arg){char buffer[64];
  // Intentionally vulnerable: classic stack overflow in a non-PIE ret2win binary.
  strcpy(buffer,arg);printf("ECHO %s\n",buffer);
}
int main(void){setvbuf(stdout,NULL,_IONBF,0);char line[1024];puts("PATCH-TUESDAY Parcel Relay v1");while(fgets(line,sizeof line,stdin)){trim(line);char *cmd=strtok(line," "),*a=strtok(NULL," "),*b=strtok(NULL,"");if(!cmd)continue;
    if(!strcmp(cmd,"REGISTER")&&a&&b){if(!valid(a)||strlen(b)<6)puts("ERR invalid registration");else puts(credentials(a,b,1)?"OK registered":"ERR exists");}
    else if(!strcmp(cmd,"LOGIN")&&a&&b){if(credentials(a,b,0)){strncpy(current_user,a,48);authenticated=1;puts("OK authenticated");}else puts("ERR bad credentials");}
    else if(!strcmp(cmd,"PUT")&&a&&b)store(a,b);
    else if(!strcmp(cmd,"GET")&&a)get(a);
    else if(!strcmp(cmd,"ECHO")&&a)echo_unsafe(a);
    else if(!strcmp(cmd,"HELP"))puts("CMDS REGISTER LOGIN PUT GET ECHO QUIT");
    else if(!strcmp(cmd,"QUIT")){puts("BYE");break;}else puts("ERR syntax");
  }return 0;}

