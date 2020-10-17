#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>

struct User {
    char name[64];
};

struct User users[5];
int usr_fds[5];
int num_usr;
int finished;

/**
 * Get the next word from the dictionary
 * @param length The length of the dictionary
 * @param dict The dictionary (array of strings)
 */
char* GetWordFromDict(int length, char** dict){
    char* ret = dict[rand()%length];
    return ret;
}

/**
 * Clears out the dictionary (as an array of calloc'd strings)
 * @param numItems the length of the dictionary
 * @param dictionary reference to the dictionary (array of strings)
 */
void FreeDictionary(int numItems, char*** dictionary){
    char** temp = *dictionary;
    for (int i = 0; i < numItems; i++){
        free(temp[i]);
    }
    free(temp);
}

/**
 * Prints out the dictionary (for debugging)
 * @param numItems the length of the dictionary
 * @param dictionary the dictionary (array of strings)
 */
void PrintDictionary(int numItems, char** dictionary){
    for (int i = 0; i < numItems; i++){
        printf("%s\n", dictionary[i]);
    }
}

/**
 * Loads the dictionary from a file
 * @param fileName Path to the dictionary file
 * @param dictionary [output] Reference to the dictionary (array of strings)
 * @param longestWordLength The longest word possible in the dictionary
 * @param numItems [output] The number of items in the dictionary
 */
void Parse(char* fileName, char*** dictionary, int longestWordLength, int* numItems){
    char** tempDictionary;

    FILE* fp = fopen(fileName, "r");
    char* line = calloc(1,longestWordLength+1);
    int currentLength = 0;
    if (fp == NULL){
        fprintf(stderr, "Error Opening file\n");
        exit(EXIT_FAILURE);
    }

    while (fgets(line,longestWordLength+2,fp)) {
        if (currentLength == 0){
            tempDictionary = calloc(1, sizeof(char*));
        }
        else{
            tempDictionary = realloc(tempDictionary, (currentLength+1)*sizeof(char*));
        }
        
        line[strlen((line))-1]='\0';
        tempDictionary[currentLength] = calloc(1,strlen(line)+1);
        strcpy(tempDictionary[currentLength],line);
        currentLength++;
        //clear up
        memset(line,'\0',longestWordLength+1);
    }
    free(line);
    fclose(fp);
    //add items for return
    *numItems = currentLength;
    *dictionary = tempDictionary;

    
}

/**
 * Handles a user connecting to the game
 *
 * @param fd The fd of the user
 * @param username The username inputted by the user
 * @returns returns this user's index in the {users} array or -1 if the fd is not found
 *
 * @todo Update {printf} calls to {send} calls
 */
int UserJoins(int fd, char* username,char* word) {
    if (strlen(username) == 0) {
        send(fd, "ERROR: username can't be empty\n",31,0);
        return 0;
    }

    for (int itr = 0; itr < strlen(username); ++itr) {
        username[itr] = tolower(username[itr]);
    }

    for (int i = 0; i < 5; ++i) {
        if (strcmp(users[i].name, username)==0) {
            char mes[256];
            memset(mes,'\0',256);
            sprintf(mes,"Username %s is already taken, please enter a different username\n", username);
            send(fd,mes,strlen(mes),0);
            return 0;
        }
    }

    for (int i = 0; i < 5; ++i) {
          if(strcmp(users[i].name,"")==0&&usr_fds[i]!=-1){
            strcpy(users[i].name, username);
            //usr_fds[i]=fd;
            char mes[128];
            memset(mes, '\0', 128);
            sprintf(mes,"Let's start playing, %s\n", username);
            send(fd,mes,strlen(mes),0);
            num_usr++;
            memset(mes, '\0', 128);
            sprintf(mes,"There are %d player(s) playing. The secret word is %lu letter(s).\n",num_usr,strlen(word));
            send(fd,mes,strlen(mes),0);
            return 1;
        }
    }

    return 0;

    //fprintf(stderr, "ERROR: we can't assign any more players\n");
}

/**
 * Handles clean up once a user is disconnected
 * @param username The username of the disconnected user
 *
 */
void UserDisconnects(char* username) {
    for (int itr = 0; itr < strlen(username); ++itr) {
        username[itr] = tolower(username[itr]);
    }
    
    for (int itr = 0; itr < 5; ++itr) {
        if (strcmp(users[itr].name, username) == 0) {
            // TODO: Clear out any other necessary user data
            strcpy(users[itr].name, "");
            usr_fds[itr] = -1;
            num_usr--;
            break;
        }
    }
}

/**
 * Should be called when there is data on the user fd
 * Note: Should only be called after the users enter the game
 * @param fd The fd of the sender
 * @param word The secret word (selected from the dictionary)
 */
void Message(int fd, char* word){
    char* username;
    char* guess_word=calloc(1025, sizeof(char));

    for(int itr=0;itr<5;++itr){
        if(fd==usr_fds[itr]) {
            username=users[itr].name;
            break;
        }
    }
    
    int n=recv(fd, guess_word, 1025, 0);
    if(n==0){  //disconnected
        //printf("i am here!\n");
        UserDisconnects(username);
        close(fd);
    }
    else{
        guess_word[strlen(guess_word)-1]='\0';
        //printf("the guess word is %s\n",guess_word);
        if(strlen(guess_word)!=strlen(word)){ //invalid guess length
            char mes[64];
            memset(mes,'\0',64);
            sprintf(mes,"Invalid guess length. The secret word is %lu letter(s).\n",strlen(word));
            send(fd,mes,strlen(mes),0);
        }
        else{ //valid guess length
            //correct character
            char* cmp_word=calloc(1,strlen(word)+1);
            strcpy(cmp_word,word);
            //printf("cmp_word is %s",cmp_word);
            int count=0, corr_plcd=0;
            int isfound;
            for(int i=0;i<strlen(guess_word);++i){
                char* new_cmp_word=calloc(1,strlen(cmp_word)+1);
                int k=0;
                isfound=0;
                for(int j=0;j<strlen(cmp_word);++j){
                    if(!isfound&&tolower(guess_word[i])==tolower(cmp_word[j])){
                        count++;
                        isfound=1;
                    }
                    else{
                        new_cmp_word[k]=cmp_word[j];
                        ++k;
                    }
                }
                free(cmp_word);
                cmp_word=new_cmp_word;
            }
            free(cmp_word);
            //correct placed
            for(int i=0;i<strlen(guess_word);++i){
  
                if(tolower(guess_word[i])==tolower(word[i])){
                    corr_plcd++;
                }
            }
            //if guess the word
            if(corr_plcd==strlen(word)){
                char mesg[128];
                memset(mesg,'\0',128);
                sprintf(mesg,"%s has correctly guessed the word %s\n",username,word);
                finished=1;
                for(int itr=0;itr<5;++itr){
                    if(strcmp(users[itr].name,"")!=0&&usr_fds[itr]!=-1){
                        int n=send(usr_fds[itr],mesg,strlen(mesg),0);
                        if(n>0){  //disconnected all users
                            strcpy(users[itr].name, "");
                            usr_fds[itr] = -1;
                            close(usr_fds[itr]);
                        }
                    }
                }
            }
            //if not guess the word
            else{
                char mesg[256];
                memset(mesg,'\0',256);
                sprintf(mesg,"%s guessed %s: %d letter(s) were correct and %d letter(s) were correctly placed.\n",username,guess_word,count,corr_plcd);
                for(int itr=0;itr<5;++itr){
                    if(strcmp(users[itr].name,"")!=0&&usr_fds[itr]!=0){
                    send(usr_fds[itr],mesg,strlen(mesg),0);
                }
            }
            
        }
        
    }
    }
    free(guess_word);
}

// Set the parameters from the command line.
void SetParms(char* argv [], int* seed, int* port, char** fileName, int* longestWordLength){
    *seed = atoi(argv[1]);
    *port = atoi(argv[2]);
    *fileName = argv[3];
    *longestWordLength = atoi(argv[4]);
}

int main(int argc, char* argv[]){
    int seed;
    int port;
    char* fileName;
    char* secret_word;
    char** dictionary;
    int longestWordLength;
    int numItems;
    int sockfd;
    struct sockaddr_in servaddr;

    //Check for number of arguments
    if (argc != 5){
        fprintf(stderr,"Wrong Number of arguments\n");
        return 1;
    }


    SetParms(argv, &seed, &port, &fileName, &longestWordLength);
    Parse(fileName, &dictionary, longestWordLength, &numItems);
    //PrintDictionary(numItems, dictionary);  //Here for debugging
    srand(seed);
    //secret_word = GetWordFromDict(numItems, dictionary);

    sockfd = socket(PF_INET, SOCK_STREAM, 0);
    //printf("%s",secret_word); //Here for debugging
    if (sockfd == -1) {
        fprintf(stderr,"Socket failed\n");
        FreeDictionary(numItems, &dictionary);
        return 1;
    }
    bzero(&servaddr, sizeof(servaddr));
    // assign IP, PORT
    servaddr.sin_family = PF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    //assign port
    servaddr.sin_port = htons(port);
    // Binding newly created socket to given IP and verification
    if ((bind(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr))) != 0) {
        fprintf(stderr,"Bind failed\n");
        FreeDictionary(numItems, &dictionary);
        return 1;
    }

    // Now server is ready to listen and verification
    if ((listen(sockfd, 5)) != 0) {
        fprintf(stderr,"Listen failed\n");
        FreeDictionary(numItems, &dictionary);
        return 1;
    }
    while(1){
        // Initialize User structs in users array
        for (int itr = 0; itr < 5; ++itr) {
            // Include any other necessary user data
            strcpy(users[itr].name, "");
        }
        secret_word = GetWordFromDict(numItems, dictionary);
        num_usr=0;
        fd_set select_fds;
        finished=0;
        for (int i = 0; i < 5; ++i) usr_fds[i] = -1;
        
        while (!finished) { // need an ender?
            int largest_fd = 0;
            
            FD_ZERO(&select_fds);
            FD_SET(sockfd, &select_fds);
            largest_fd = sockfd;
            for (int i = 0; i < 5; ++i) {
                if (usr_fds[i] != -1) {
                    FD_SET(usr_fds[i], &select_fds);
                    if (usr_fds[i] > largest_fd) {
                        largest_fd = usr_fds[i];
                    }
                }
            }
            //printf("waiting on select for fds, largest: %d...\n", largest_fd);
            int result = select(largest_fd + 1, &select_fds, NULL, NULL, NULL);
            //printf("select completed with %d results\n", result);
            if (result == -1) {
                fprintf(stderr, "Select failed\n");
                FreeDictionary(numItems, &dictionary);
                return 1;
            }
            if (num_usr<5&&FD_ISSET(sockfd, &select_fds)) {
                // user connecting to server, accept the connection
                int client_fd = accept(sockfd, NULL, NULL);
                if (client_fd < 0) {
                    fprintf(stderr, "Accept failed\n");
                    FreeDictionary(numItems, &dictionary);
                    return 1;
                }
                
                //bool set_usr_fd = false;
                for (int i = 0; i < 5; ++i) {
                    if (usr_fds[i] == -1) {
                        usr_fds[i] = client_fd;
                        //set_usr_fd = true;
                        break;
                    }
                }
               
                    char mes[64];
                    memset(mes,'\0',64);
                    sprintf(mes,"Welcome to Guess the Word, please enter your username.\n");
                    send(client_fd,mes,strlen(mes),0);
                           
                       }

        
            for (int i = 0; i < 5; ++i) {
                if (usr_fds[i] != -1 && FD_ISSET(usr_fds[i], &select_fds)) {
                    if (strcmp(users[i].name, "") == 0) { // waiting for username
                        char username[64];
                        memset(username,'\0',64);
                        int n = recv(usr_fds[i], username, 64, 0);
                        if (n == 0) { // user disconnected before sending username
                            usr_fds[i] = -1;
                            close(usr_fds[i]);
                        } else {
                            //strcpy(users[i].name, username);
                            //printf("username is %s",username);
                            username[strlen(username)-1]='\0';
                            UserJoins(usr_fds[i], username,secret_word);
                        }
                    } else { // waiting for message
                                // user sent a message
                                    Message(usr_fds[i], secret_word);
                                }
                            
                    
                }
            }
        }
    }
    //free the used memory
    FreeDictionary(numItems, &dictionary);
    return 0;
}
