#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

struct User {
    char name[1024];
};

struct User users[5];
int usr_fds[5];

char* GetWordFromDict(int length, char** dict){
    char* ret = dict[rand()%length];
    return ret;
}

void FreeDictionary(int numItems, char*** dictionary){
    char** temp = *dictionary;
    for (int i = 0; i < numItems; i++){
        free(temp[i]);
    }
    free(temp);
}

// Here for debugging and Testing
void PrintDictionary(int numItems, char** dictionary){
    for (int i = 0; i < numItems; i++){
        printf("%s\n", dictionary[i]);
    }
}

// Load dictionary
void Parse(char* fileName, char*** dictionary, int longestWordLength, int* numItems){
    char** tempDictionary;

    FILE* fp = fopen(fileName, "r");
    char* line = calloc(longestWordLength, 1);
    int currentLength = 0;
    if (fp == NULL){
        fprintf(stderr, "Error Opening file\n");
        exit(EXIT_FAILURE);
    }
    while (fgets(line,longestWordLength,fp)) {
                if (currentLength == 0){
                    tempDictionary = calloc(1, sizeof(char*));
                }
                else{
                    tempDictionary = realloc(tempDictionary, (currentLength+1)*sizeof(char*));
                }
                tempDictionary[currentLength] = calloc(strlen(line)+1,1);
                strcpy(tempDictionary[currentLength],line);
                currentLength++;
              //clear up
                memset(line,'\0',longestWordLength);
        }
        free(line);
        fclose(fp);
        *numItems = currentLength;
        *dictionary = tempDictionary;
}


/*this function handle each message from the users after they enter the game*/
void Message(char* userid, int fd, char* word){
    char* guess_word=calloc(1,1025);
    for(int itr=0;itr<5;++itr){
        if(fd==usr_fds[itr]) {
            username=users[itr].name;
            break;}
    }
    
    int n=recv(fd, guess_word, 1025, 0);
    if(n==0){  //disconnected
        UserDisconnects(username);
        close(fd);
    }
    else{
        guess_word[strlen(guess_word)-1]='\0';
        if(strlen(guess_word)!=strlen(word)){ //invalid guess length
            char mes[64];
            sprintf(s,"Invalid guess length. The secret word is %lu letter(s)",strlen(word));
            send(fd,mes,strlen(mes),0);
        }
        else{ //valid guess length
            //correct character
            char* cmp_word=calloc(1,strlen(word));
            strcpy(cmp_word,word);
            int count=0, corr_plcd=0;
            
            for(int i=0;i<strlen(guess_word)-1;++i){
                char* new_cmp_word=calloc(1,strlen(cmp_word));
                int k=0;
                for(int j=0;j<strlen(cmp_word);++j){
                    if(tolower(guess_word[i])==tolower(cmp_word[j])){
                        count++;
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
            for(int i=0;i<strlen(guess_word)-1;++i){
  
                if(tolower(guess_word[i])==tolower(word[i])){
                    corr_plcd++;
                }
            }
            //if guess the word
            if(corr_plcd==strlen(word)){
                char mesg[2048];
                sprintf(mesg,"%s has correctly guessed the word %s",username,word);
                for(int itr=0;itr<5;++itr){
                    if(strcmp(users[itr].name,"")!=0&&usr_fds[itr]!=0){
                        int n=send(usr_fds[itr],mesg,strlen(mesg),0);
                        if(n>0){  //disconnected all users
                            strcpy(users[itr].name, "");
                            bzero(&usr_fds[itr],sizeof(int));
                            close(usr_fds[itr]);
                        }
                    }
                }
            }
            //if not guess the word
            else{
                char mesg[2048];
                sprintf(mesg,"%s guessed %s: %d letter(s) were correct and %d letter(s) were correctly placed",username,guess_word,count,corr_plcd);
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

/**
 * Handles a user connecting to the game
 * 
 * @param username The username inputted by the user
 * @returns -1 if {username} isn't valid or taken, else returns this user's index in the {users} array
 * 
 * @todo Update {printf} calls to {send} calls
 */
int UserJoins(char* username) {
    if (strlen(username) == 0) {
        fprintf(stderr, "ERROR: username can't be empty\n");
        return -1;
    }

    for (int itr = 0; itr < strlen(username); ++itr) {
        username[itr] = tolower(username[itr]);
    }

    int unoccupied = -1;
    for (int itr = 0; itr < 5; ++itr) {
        if (unoccupied == -1 && strlen(users[itr].name) == 0) {
            unoccupied = itr;
        } else if (strcmp(users[itr].name, username) == 0) {
            printf("Username %s is already taken, please enter a different username\n", username);
                    
            return -1;
        }
    }

    if (unoccupied != -1) {
        // TODO: Add any other necessary user data
        strcpy(users[unoccupied].name, username);
        printf("Let's start playing, %s\n", username);
    } else {
        fprintf(stderr, "ERROR: we can't assign any more players\n");
        return -1;
    }
}

// Set the parameters from the command line.
void SetParms(char* argv [], int* seed, int* port, char** fileName, int* longestWordLength){
    *seed = atoi(argv[1]);
    *port = atoi(argv[2]);
    *fileName = argv[3];
    *longestWordLength = atoi(argv[4]);
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
            bzero(&usr_fds[itr],sizeof(int));
            break;
        }
    }
}

int main(int argc, char* argv[]){
    int seed;
    int port;
    char* fileName;
    char* word;
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

    // Initialize User structs in users array
    for (int itr = 0; itr < 5; ++itr) {
        // Include any other necessary user data
        strcpy(users[itr].name, "");
    }

    SetParms(argv, &seed, &port, &fileName, &longestWordLength);
    Parse(fileName, &dictionary, longestWordLength, &numItems);
    //PrintDictionary(numItems, dictionary);  //Here for debugging
    srand(seed);
    word = GetWordFromDict(numItems, dictionary);
    sockfd = socket(AF_INET, SOCK_STREAM, 0); 
    //printf("%s\n",word); //Here for debugging
    if (sockfd == -1) { 
        fprintf(stderr,"Socket failed\n"); 
        return 1;
    } 
    bzero(&servaddr, sizeof(servaddr));
    // assign IP, PORT 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    //assign port
    servaddr.sin_port = htons(port);
    // Binding newly created socket to given IP and verification 
    if ((bind(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr))) != 0) { 
        fprintf(stderr,"Bind failed\n"); 
        return 1;
    } 

    // Now server is ready to listen and verification 
    if ((listen(sockfd, 5)) != 0) { 
        fprintf(stderr,"Listen failed\n"); 
        return 1;
    } 
    FreeDictionary(numItems, &dictionary);
    return 0;
}
