#ifndef __PROJ2_H__
#define __PROJ2_H__

#include <stdio.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/sem.h>
#include <stdlib.h>
#include <errno.h>
#include <signal.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <semaphore.h>
#include <pthread.h>

#define _GNU_SOURCE

// Datova struktura obsahujuca ukazatele na zdielanu pamat, semafory a ID zdielanej pamate
typedef struct shdata
{
	int shmid;
	int shm_action;
	int shm_NE;
	int shm_NC;
	int shm_NB;
	int shm_writer;
	int shm_blocker;
	int shm_decision;
	int shm_certificates;
	int shm_cer;
	int *action;
	int *NE;
	int *NC;
	int *NB;
	int *cer;
	sem_t *writer;
	sem_t *blocker;
	sem_t *decision;
	sem_t *certificates;
} shdata;

// Globalna datova struktura obsahujuca vsetky ukazatele na semafory, zdielanu pamat a ID zdielanych pamati. Pri vypracovavani ulohy som mal casto
// problem stym ze sa shared memory segmenty pri chybnom ukonceni (/neukonceni) nevymazali, a potom som ich musel vzdy mazat rucne. Pomocou tejto datovej
// struktury a SIGINT handleru sa vsak uz dalo pri chybovom ukonceni jednoducho programu poslat SIGINT a SIGINT handler tuto datovu strukturu a aj vsetku zdielanu pamat vymazal.
shdata *data;

//Funkcia vymaze zdielanu pamat a semafory v pripade potreby ukoncenia procesu.
void ErrnoExit(shdata *data);

//SIGINT handler, v pripade ze je programu poslany signal SIGINT zavola funkciu ErrnoExit, vymaze zdielanu pamat a ukonci program.
void HandleSigint(int sig);

//Funkcia na kontrolu spravneho poctu argumentov. Taktiez kontroluje ci su zadane cisla v rozsahu 0 - 2000. Vracia 0 v pripade ze su
// zadane argumenty v nespravnom formate a vracia 1 ak su zadane argumenty spravne.
int ArgCheck(int argc, char *argv[]);

//Funkcia generuje pseudo-nahodne cislo, vola sa ked maju procesy cakat nahodnu dobu zo zadaneho intervalu. Vracia cislo zo zadaneho intervalu.
int IntRandom(int lower, int upper);

int ArgCheck(int argc, char *argv[])
{
	if(argc != 6)
	{
		fprintf(stderr,"Chyba: nespravny pocet argumentov.\n");
		return 0;
	}
	
	for(int i = 1; i<argc; i++)
	{
		for(unsigned int j = 0; j<strlen(argv[i]); j++)
		{
			if(!isdigit(argv[i][j]))
			{
				fprintf(stderr,"Chyba: argumenty musia byt iba cele cisla.\n");
				return 0;
			}
		}
	}

	if((strtol(argv[1], NULL, 10) < 1) || ((strtol(argv[2], NULL, 10) < 0) || (strtol(argv[2], NULL, 10) > 2000)) || ((strtol(argv[3], NULL, 10) < 0) || (strtol(argv[3], NULL, 10) > 2000)) || ((strtol(argv[4], NULL, 10) < 0) || (strtol(argv[4], NULL, 10) > 2000)) || ((strtol(argv[5], NULL, 10) < 0) || (strtol(argv[5], NULL, 10) > 2000)))
	{
		fprintf(stderr, "Prekroceny implementacny limit. Pocet immigrantov musi byt vacsi ako nula a doba cakania vsetkych procesov musi byt z intervalu <0, 2000> ms\n");
		return 0;
	}
	return 1;
}

int IntRandom(int lower, int upper) 
{ 
	if (upper == 0)
	{
		return 0;
	}
    int num = (rand() % (upper - lower + 1)) + lower; 
	return num;
} 

void ErrnoExit(shdata *data)
{
	shmdt(data->action);
	shmdt(data->NE);
	shmdt(data->NC);
	shmdt(data->NB);
	shmdt(data->writer);
	shmdt(data->blocker);
	shmdt(data->decision);
	shmdt(data->certificates);
	sem_destroy(data->writer);
	sem_destroy(data->blocker);
	sem_destroy(data->decision);
	sem_destroy(data->certificates);
	shmdt(data->cer);
	shmctl(data->shm_cer, IPC_RMID, NULL);
	shmctl(data->shmid, IPC_RMID, NULL);
	shmctl(data->shm_action, IPC_RMID, NULL);
	shmctl(data->shm_NE, IPC_RMID, NULL);
	shmctl(data->shm_NC, IPC_RMID, NULL);
	shmctl(data->shm_NB, IPC_RMID, NULL);
	shmctl(data->shm_writer, IPC_RMID, NULL);
	shmctl(data->shm_blocker, IPC_RMID, NULL);
	shmctl(data->shm_decision, IPC_RMID, NULL);
	shmctl(data->shm_certificates, IPC_RMID, NULL);
	free(data);
}

void HandleSigint(int sig)
{
	fprintf(stderr,"Caught signal %d\n",sig);
	ErrnoExit(data);
	exit(1);
}

#endif // __PROJ_H__