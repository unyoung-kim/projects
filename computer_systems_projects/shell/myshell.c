#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <stdbool.h>
#include <fcntl.h>

/*
Print message

Parameter: 
msgm - Message that will be printed
*/
void myPrint(char *msg)
{
    write(STDOUT_FILENO, msg, strlen(msg));
}

/*
Print Error Message
*/
void printError()
{
    char error_message[30] = "An error has occurred\n";
    write(STDOUT_FILENO, error_message, strlen(error_message));
}

/*
Split a string into tokens using a delimitor

<Parameters>
single_cmd: A single command string
arg_count: Number of arguments in the command
split: Delimitor

<Return>
Array of tokens of a command
*/
char** break_cmd(char* single_cmd, int *arg_count, char* split){
    //count the number of tokens
    char *tracker2;
    char *tracker3;
    char *cmd_cpy = (char*)strdup(single_cmd);
    char *tkn = strtok_r(cmd_cpy, split, &tracker2);
    int count = 0;
    
    //Count the number of tokens in a command
    while(tkn != NULL){
        count++;
        tkn = strtok_r(NULL, split, &tracker2);
    }
    free(cmd_cpy);
    
    //Separate tokens into array of strings
    char **args = malloc(sizeof(char*) * (count+1));
    char *arg = strtok_r(single_cmd, split, &tracker3);
    int n = 0;
    
    while(arg != NULL){
        args[n] = arg;
        arg = strtok_r(NULL, split, &tracker3);
        n++;
    }
    args[n] = NULL;
    *arg_count = count;
    
    return args;
}

/*
Execute a given command. There are only three built-in commands - exit, cd, pwd.

<Parameters>
argv: array of tokens of a command

*/
void execute_cmd(char *argv[]){
    if(!strcmp(argv[0], "exit")){
        if(argv[1] == NULL){
            exit(0);
        } else{
            printError();
        }
    } else if(!strcmp(argv[0], "pwd")){
        char cwd[256];
        if (getcwd(cwd, sizeof(cwd)) == NULL){
            printError();
        } else if(argv[1] != NULL){
            printError();
        } else{
            myPrint(cwd);
            myPrint("\n");
        }
    } else if(!strcmp(argv[0], "cd")){
        if(argv[1] == NULL){
            char *home = getenv("HOME");
            if(home == NULL){
                printError();
            } else{
                chdir(home);
            }
        } else{
            if(strcmp(argv[1], "/")){
                int ret = chdir(argv[1]);
                if(ret == -1){
                    printError();
                }
            } else {
                if(argv[2] != NULL){
                    if(!strcmp(argv[2], "/")){
                        printError();
                    } 
                } else{
                    int ret2 = chdir(argv[1]);
                    if(ret2 == -1){
                        printError();
                    }
                }
            }
        } 
    } else{
        int ret = fork();
        if(ret == 0){
            int exec = execvp(argv[0], argv);
            if(exec == -1){

                printError();
                exit(0);
            } 
        } else if(ret == -1){
            
        } else{
            wait(&ret);
        }
    }
}

/*
Check if there is only one redirection symbol. Replace the redirection symbol with null terminator

<Parameters>
cmd: Command
redirect_index: 1 for Redirection(>), 2 for Advanced Redirection(>+), 4 for incorrect format
redirect_pos: Position of Redirection symbol within a command

<Return>
Command with > or >+ replaced with a NULL terminator
*/
char *check_redirect(char *cmd, int *redirect_index, int *redirect_pos){
    int i = 0;
    int count = 0;

    //Check if there is > or >+ the command. If yes how many(error when more than 1)
    while(cmd[i]!='\0'){
        if((cmd[i] == '>') && (cmd[i+1] == '+')){
            count++;
            cmd[i] = '\0';
            *redirect_index = 2;
            *redirect_pos = i;
        }else if(cmd[i] == '>'){
            count++;
            cmd[i] = '\0';
            *redirect_index = 1;
            *redirect_pos = i;
        } 
        i++;
    }

    //More than one redirection command: error case
    if(count > 1){
        *redirect_index = 4;
    }

    return cmd;  
}

/*
Redirect standard output

<Parameters>
argv: Command
outputfile: file that the standard output is being redirected to
fd: file descriptor index

<Return>
1 if redirection is successful, 0 if not
*/
int redirection(char *argv[], char *outputfile[], int *fd){

    *fd=open(outputfile[0], O_CREAT|O_WRONLY|O_EXCL, S_IRUSR | S_IWUSR);

    if(*fd < 0){
        return 0;
    }

    dup2(*fd,1); 
    return 1;
}

/*
Check that the redirection command does not include built in functions

<Parameters>
cmd_args: Command
o_file: output file

<Return>
True if redirection command does not include built-in functions, False if not
*/
bool check_redir_format(char **cmd_args, char **o_file){
    if ((cmd_args[0] == NULL)|| (o_file[0] == NULL)){

        return false;
    }
    //Use Built in Function 
    if(!strcmp(cmd_args[0], "cd") || !strcmp(cmd_args[0], "pwd") || !strcmp(cmd_args[0], "exit")){

        return false;
    }  
    return true;
}

/*
Execute a single line of command. Within in a single line of command multiple commands can be separated by ';' 

<Parameters>
pinput: Input line from the user

*/
void execute_cmd_line(char *pinput){
    //Execute A Line of Command(s)
    if (!pinput) {
        exit(0);
    } else{
        //Parsing
        char *tracker1;
        char *single_cmd = strtok_r(pinput, ";\n", &tracker1);

        while(single_cmd != NULL){

            //Check if the command has > or >+
            int redirect_index = 0;
            int redirect_pos;
            int arg_count;
            int file_count;
            char *cmd = check_redirect(single_cmd, &redirect_index, &redirect_pos);

            if(redirect_index == 0){
                //Normal Command
                char** cmd_args = break_cmd(single_cmd, &arg_count," \t"); 

                if(cmd_args[0] != NULL){
                    execute_cmd(cmd_args);
                }

                
                free(cmd_args);

            } else if(redirect_index == 1){
                //Normal Redirection
                int stdout_copy = dup(1);

                char** cmd_args = break_cmd(cmd, &arg_count," \t");
                char **o_file = break_cmd(cmd+redirect_pos+1, &file_count, " \t");
                //Wrong Input (e.g. >, ls > , cd > a)
                bool redir_format = check_redir_format(cmd_args, o_file);            
                
                if(file_count != 1 || redirect_index == 4 || redir_format==0){
                    printError();
                } else{
                    int fd;
                    int file_exist = redirection(cmd_args, o_file, &fd);

                    if(file_exist){
                        execute_cmd(cmd_args);
                    }else{
                        printError();
                    }      

                    if (fd > 0) {
                        int retval = close(fd);
                        if(retval<0){
                            printError();
                        }
                    } 
                }

                dup2(stdout_copy,1);
                free(cmd_args);
                    
            } else if(redirect_index == 2){ 
                //ADVANCED REDIRECTION

                char** cmd_args = break_cmd(cmd, &arg_count," \t");
                char **o_file = break_cmd(cmd+redirect_pos+2, &file_count, " \t");

                bool redir_format = check_redir_format(cmd_args, o_file);

                if( file_count != 1 || redir_format == 0){
                    printError();
                } else {
                    int stdout_copy = dup(1);
                    char buffer[100];
                    //Open temp

                    int temp=open(".temp", O_CREAT|O_WRONLY|O_RDONLY, S_IRUSR | S_IWUSR);
                    if (temp < 0){
                        printError();
                    }

                    dup2(temp,1); 
                    execute_cmd(cmd_args);
                    dup2(stdout_copy,1);

                    //Return to Parent Process
                    int retval1=close(temp);
                    if(retval1<0){
                        printError();
                    } 

                    //Reopen temp with new end of file offset with O_APPEND mode
                    int temp_reopen=open(".temp", O_WRONLY|O_RDONLY|O_APPEND, S_IRUSR | S_IWUSR);
                    if (temp_reopen < 0){
                        printError();
                    }

                    int fd = open(o_file[0], O_CREAT|O_RDONLY, S_IRUSR | S_IWUSR);
                    
                    int n_read = read(fd, buffer, 100);
                    while(n_read > 0){
                        write(temp_reopen, buffer, n_read);
                        n_read = read(fd, buffer, 100);
                    }

                    rename(".temp", o_file[0]);
                    //Close   
                    int retval=close(fd);
                    if(retval<0){
                        printError();
                    } 
                    //Close
                    int retval2=close(temp_reopen);
                    if(retval2<0){
                        printError();
                    } 
                }

                
                free(cmd_args);

            } else{
                printError();
            }
            //Get new command
            single_cmd = strtok_r(NULL, ";\n", &tracker1);
            
        }
    }
}
/*
Check if the command line has a valid format. Print error messages if the input is invalid

<Parameters>
pinput: Input command from the user

<Return>
0 if the command is out of length, 1 if the command is empty, 2 if the command is valid
*/

int check_cmd_condition(char *pinput){
//0: Error but still print command, 1: No error but don't print command, 2: Print and Execute command

    //Length Check 
    if(strlen(pinput)>=513 && pinput[strlen(pinput)-1] != '\n'){
        return 0;
    }
    //Empty Command Check
    if(!strcmp(pinput, "\n")){
        return 1;
    }
    int i = 0;
    while(pinput[i] == ' ' || pinput[i] == '\t'){
        i++;
    }
    if (pinput[i]=='\n'){
        return 1;
    }

    return 2;
}


int main(int argc, char *argv[]) 
{
    char cmd_buff[514];
    char *pinput;
    
    
    while (1) {

        if(argc == 1){
            //Interactive Mode
     
                myPrint("myshell> ");
                pinput = fgets(cmd_buff, 514, stdin);
                //Check the length of the command
                if(strlen(pinput)>=513 && pinput[strlen(pinput)-1] != '\n'){
                    printError();
                    pinput = fgets(cmd_buff, 514, stdin);
                } else {
                    //Execute Command
                    execute_cmd_line(pinput);
                }

        }else if(argc == 2){
            //Batch Mode
                //If Batch Mode, read the commands from the file
                FILE *input_file = fopen(argv[1], "r");
                if(input_file==NULL){
                    printError();
                    exit(0);
                }
                
                while((pinput = fgets(cmd_buff, 514, input_file)) != NULL){
                    int cond = check_cmd_condition(pinput);
                    //printf("LENGTH: %ld\n", strlen(pinput));
                    //Wrong Length
                    if(cond == 0){
                        while(1){
                                myPrint(pinput);
                                pinput=fgets(cmd_buff, 514, input_file);
                                if(pinput == NULL || pinput[strlen(pinput)-1] == '\n'){
                                    myPrint(pinput);
                                    //myPrint("\n");
                                    printError();
                                    break;
                                
                            }
                            
                        }
                    
                    } else if(cond == 1){ //Empty command line

                    } else{
                        myPrint(pinput);
                        execute_cmd_line(pinput);
                    }
                }
                //End of File
                if (pinput == NULL){
                    exit(0);
                }
            
        } else{
            printError();
            exit(0);
        }
    }
}

