#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lib/unp.h"//for my machine
//#include "unp.h" //for submitty

char* GetWordFromDict(int length, char** dict){
	char* ret = dict[rand()%length];
	return ret;
}

//Set the parameters from the command line.
void SetParms(char* argv [], int* seed, int* port, char** fileName, int* longestWordLength){
	*seed = atoi(argv[1]);
	*port = atoi(argv[2]);
	*fileName = argv[3];
	*longestWordLength = atoi(argv[4]);
}



void FreeDictionary(int numItems, char*** dictionary){
	char** temp = *dictionary;
	for (int i = 0; i < numItems; i++){
		free(temp[i]);
	}
	free(temp);
}



//Here for debugging and Testing
void PrintDictionary(int numItems, char** dictionary){
	for (int i = 0; i < numItems; i++){
		printf("%s\n", dictionary[i]);
	}
}

//Load dictionary
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
    }
    free(line);
    fclose(fp);
    *numItems = currentLength;
    *dictionary = tempDictionary;
}

void Message(char* userid, int fd){

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