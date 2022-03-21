# Creating a Shell

The shell should operate in this basic way: when you type in a command (in response to its prompt), the shell creates a child process that executes the command you entered and then prompts for more user input when it has finished. The shell will be similar to, but much simpler than, the one in Unix. 

## Functionalities:
#### - Parsing a Command Line
The shell can parse a command, and run the program corresponding to the command. For example, if the user types "ls -la /tmp" , the shell runs the ls program with all the given arguments and print the output on the screen.

The maximum length of a command line the shell can take is 512 bytes (excluding the newline).

#### - Multiple Commands
Use the ";" character to separate multiple jobs on a single command line.

For example, if the user types "ls; ps; who" , the jobs should be run one at a time, in left-to-right order. Hence, in our previous example ( "ls; ps; who" ), first ls should run to completion, then ps , then who . The prompt should not be shown again until all jobs are complete.

#### - Redirection (">")
Allows the users to send the output of his/her program to a file rather than to the screen. The UNIX shell provides this feature with the ">" character.

For example, if a user types "ls -la /tmp > output" , nothing should be printed on the screen. Instead, the output of the ls program should be rerouted to the output file.

#### - Advanced Redirection (">+")
It will insert the program's output to the beginning of the outputFile without overwriting the old content. That is the old content will be shifted.

If the outputFile does not exist, ">+" will behave like ">".

This is a feature that does not exist in typical shell programs. That is, ">" overwrites the output file and ">>" appends to the end of the output file (in this project you don't need to support ">>"). But, there is no support to "insert" the output to the beginning of the file.

#### - Batch Mode
To make testing much faster, shell supports batch mode.
