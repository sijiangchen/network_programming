#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct User {
  char name[1024];
};

struct User users[5];

char* GetWordFromDict(int index, char** dict){

}

//Load dictionary
void Parse(){

}

void Message(char* userid, int fd){

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

	return unoccupied;
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
      break;
    }
  }
}

int main(int argc, char* argv[]) {
	// Initialize User structs in users array
  for (int itr = 0; itr < 5; ++itr) {
		// Include any other necessary user data
    strcpy(users[itr].name, "");
  }

  return 0;
}