#include "proj2.h"


int main(int argc, char *argv[])
{
	if(!ArgCheck(argc, argv))
	{
		return 1;
	}

	data = malloc(sizeof(shdata));
	signal(SIGINT, HandleSigint);
	key_t key = ftok(argv[0], 'A');
	key_t action_key = ftok(argv[0], 'B');
	key_t NE_key = ftok(argv[0], 'C');
	key_t NC_key = ftok(argv[0], 'D');
	key_t NB_key = ftok(argv[0], 'E');
	key_t writer_key = ftok(argv[0], 'F');
	key_t blocker_key = ftok(argv[0], 'G');
	key_t decision_key = ftok(argv[0], 'H');
	key_t certificates_key = ftok(argv[0], 'I');
	key_t cer_key = ftok(argv[0], 'J');	

	if(errno)
	{
		free(data);
		fprintf(stderr,"Error, errno set on line 24, ftok\n");
		return 1;
	}
	
	data->shmid = shmget(key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_action = shmget(action_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_NE = shmget(NE_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_NC = shmget(NC_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_NB = shmget(NB_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_writer = shmget(writer_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_blocker = shmget(blocker_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_decision = shmget(decision_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_certificates = shmget(certificates_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);
	data->shm_cer = shmget(cer_key, 1024, 0644 | IPC_CREAT | IPC_EXCL);

	if(errno)
	{
		shmctl(data->shmid, IPC_RMID, NULL);
		shmctl(data->shm_action, IPC_RMID, NULL);
		shmctl(data->shm_NE, IPC_RMID, NULL);
		shmctl(data->shm_NC, IPC_RMID, NULL);
		shmctl(data->shm_NB, IPC_RMID, NULL);
		shmctl(data->shm_writer, IPC_RMID, NULL);
		shmctl(data->shm_blocker, IPC_RMID, NULL);
		shmctl(data->shm_decision, IPC_RMID, NULL);
		shmctl(data->shm_certificates, IPC_RMID, NULL);
		shmctl(data->shm_cer, IPC_RMID, NULL);
		free(data);
		fprintf(stderr,"Error, errno was set, on line 42\n");
		return 1;
	}

	data->action = shmat(data->shm_action, 0, 0);
	data->NE = shmat(data->shm_NE, 0, 0);
	data->NC = shmat(data->shm_NC, 0, 0);
	data->NB = shmat(data->shm_NB, 0, 0);
	data->cer = shmat(data->shm_cer, 0, 0);
	data->writer = shmat(data->shm_writer, 0, 0);
	data->blocker = shmat(data->shm_blocker, 0, 0);
	data->decision = shmat(data->shm_decision, 0, 0);
	data->certificates = shmat(data->shm_certificates, 0, 0);

	if(errno)
	{
		shmdt(data->action);
		shmdt(data->NE);
		shmdt(data->NC);
		shmdt(data->NB);
		shmdt(data->writer);
		shmdt(data->blocker);
		shmdt(data->decision);
		shmdt(data->certificates);
		shmdt(data->cer);
		shmctl(data->shmid, IPC_RMID, NULL);
		shmctl(data->shm_action, IPC_RMID, NULL);
		shmctl(data->shm_NE, IPC_RMID, NULL);
		shmctl(data->shm_NC, IPC_RMID, NULL);
		shmctl(data->shm_NB, IPC_RMID, NULL);
		shmctl(data->shm_writer, IPC_RMID, NULL);
		shmctl(data->shm_blocker, IPC_RMID, NULL);
		shmctl(data->shm_decision, IPC_RMID, NULL);
		shmctl(data->shm_certificates, IPC_RMID, NULL);
		shmctl(data->shm_cer, IPC_RMID, NULL);
		free(data);
		fprintf(stderr,"Error, errno was set, on line 69\n");
		return 1;
	}

	sem_init(data->writer, 1, 1); //Semafor sluzi na synchronizaciu vypisov a inkrementacie shared premennych.
	sem_init(data->blocker, 1, 1); //Semafor sluzi na zablokovanie vchodu do budvy sudcom a aj zabezpecenie ze do budovy vzdy vchadza iba 1 osoba naraz.
	sem_init(data->decision, 1, 0); //Semafor sluzi na informovanie sudcu o tom ze vsetci imigranti v budove su uz zaregistrovany a moze pokracovat.
	sem_init(data->certificates, 1, 0); // Semafor uvolnuje sudca po vydani rozhodnuti. Je inicializovany na 0, aby ho mohol sudca vzdy uvolnit.
										// Imigranti si ho nasledne beru a uvolnuju, az dokym nedojde ku poslednemu imigrantovi, ktory ho znovu zamkne.

	if(errno)
	{
		ErrnoExit(data);
		fprintf(stderr,"Error, errno was set, on line 101, sem_init\n");
		return 1;
	}

	FILE *file = fopen("proj2.out", "w");
	setbuf(file, NULL);
	
	if(errno)
	{
		fclose(file);
		ErrnoExit(data);
		fprintf(stderr,"Error, errno was set, on line 111, fopen\n");
		return 1;
	}
	*(data->cer) = 0;
	*(data->action) = 1;
	*(data->NE) = 0;
	*(data->NC) = 0;
	*(data->NB) = 0;
	int i = 1;
	int k;
	pid_t judge, immigrant;
	immigrant = fork(); //Vytvarame child proces na generovanie imigrantov.
	if(errno)
	{
		fclose(file);
		ErrnoExit(data);
		fprintf(stderr,"Error, errno was set, on line 127, fork\n");
		return 1;
	}
	if(immigrant) // Iba pre hlavne parent proces.
	{
		judge = fork(); // Vytvarame proces sudcu.
		if(errno)
		{
			fclose(file);
			ErrnoExit(data);
			fprintf(stderr,"Error, errno was set, on line 137, fork\n");
			return 1;
		}
		goto judgement; // Skaceme na kod pre podproces sudcu. Bolo by ho mozne uviest aj rovno tu, no skok mi prisiel prehladnejsi kedze sme ako prvy vytvorili podproces
						// na generovanie imigrantov.
	}

	if(!immigrant) //Generator imigrantov.
	{
		pid_t imm;
		while(i < strtol(argv[1], NULL, 10)+1)
		{
			if (strtol(argv[2], NULL, 10) != 0)
			{
				usleep(IntRandom(0, 1000 * strtol(argv[2], NULL, 10)));
			}
			if((imm = fork()) == 0)	//Generujeme imigrantov. Ti vykonaju vetvu if (vypis) a breaknu sa z cyklu von.
			{
				sem_wait(data->writer);
				fprintf(file,"%d : IMM %d : starts\n", *(data->action), i);
				*(data->action) = *(data->action) + 1;
				sem_post(data->writer);

				break;
			}
			if(errno)
			{
				fclose(file);
				ErrnoExit(data);
				fprintf(stderr,"Error, errno was set, on line 166, fork\n");
				return 1;
			}
			i++;
		}
		if (imm) // Po ukonceni generovanie proces generujuci imigrantov vykona wait() pre kazdy proces imigranta ktory vygeneroval a nasledne skonci.
		{
			for(int j = 0; j<strtol(argv[1], NULL, 10); j++)
			{
				wait(NULL);
				if(errno)
				{
					fclose(file);
					ErrnoExit(data);
					fprintf(stderr,"Error, errno was set, on line 179, wait\n");
					return 1;
				}
			}
			fclose(file);
			ErrnoExit(data);
			exit(0);
		}


		// Tu pokracuju procesy imigrantov po vyskoceni z cyklu.

		sem_wait(data->blocker);
		sem_wait(data->writer);
		*(data->NE) = *(data->NE) + 1;
		*(data->NB) = *(data->NB) + 1;
		fprintf(file,"%d : IMM %d : enters : %d : %d : %d\n", *(data->action), i, *(data->NE), *(data->NC), *(data->NB));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);
		sem_post(data->blocker);

		sem_wait(data->writer);
		*(data->NC) = *(data->NC) + 1;
		k = *(data->NC);
		fprintf(file,"%d : IMM %d : checks : %d : %d : %d\n", *(data->action), i, *(data->NE), *(data->NC), *(data->NB));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);

		if((*(data->NE) == k) && (*(data->NE) != 0) && (*(data->NE) == *(data->NC))) //Vsetci imigranti v budove su zaregistrovani
		{
			sem_post(data->decision);
		}

		sem_wait(data->certificates);

		*(data->cer) = *(data->cer) - 1;

		if(*(data->cer)>0)
		{
			sem_post(data->certificates);
		}

		sem_wait(data->writer);
		fprintf(file,"%d : IMM %d : wants certificate : %d : %d : %d\n", *(data->action), i, *(data->NE), *(data->NC), *(data->NB));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);

		if (strtol(argv[4], NULL, 10) != 0)
		{
			usleep(IntRandom(0, 1000 * strtol(argv[4], NULL, 10)));
		}

		sem_wait(data->writer);
		fprintf(file,"%d : IMM %d : got certificate : %d : %d : %d\n", *(data->action), i, *(data->NE), *(data->NC), *(data->NB));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);

		sem_wait(data->blocker);
		sem_wait(data->writer);
		*(data->NB) = *(data->NB) - 1;
		fprintf(file,"%d : IMM %d : leaves : %d : %d : %d\n", *(data->action), i, *(data->NE), *(data->NC), *(data->NB));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);
		sem_post(data->blocker);

		fclose(file);
		ErrnoExit(data);
		exit(0);
	}

judgement:
	if(!judge) //Podproces sudcu zacina tu. Hlavny proces celu tuto vetvu preskoci.
	{
		int total = 0;
		while(total<strtol(argv[1], NULL, 10)) //Kod sudcu sa opakuje v cykle az dokym nevydal rozhodnutia pre vsetkych imigrantov.
		{
			if (strtol(argv[3], NULL, 10) != 0)
			{
				usleep(IntRandom(0, 1000 * strtol(argv[3], NULL, 10)));
			}

			sem_wait(data->writer);
			fprintf(file,"%d : JUDGE : wants to enter\n", *(data->action));
			*(data->action) = *(data->action) + 1;
			sem_post(data->writer);

			sem_wait(data->blocker);
			sem_wait(data->writer);
			fprintf(file,"%d : JUDGE : enters : %d : %d : %d\n", *(data->action), *(data->NE), *(data->NC), *(data->NB));
			*(data->action) = *(data->action) + 1;
			sem_post(data->writer);

			sem_wait(data->writer);
			if(*(data->NE) != *(data->NC)) //Ak niesu vsetci imigranti zaregistrovani
			{
				fprintf(file,"%d : JUDGE : waits for imm : %d : %d : %d\n", *(data->action), *(data->NE), *(data->NC), *(data->NB));
				*(data->action) = *(data->action) + 1;
				sem_post(data->writer);

				if(*(data->NE) == 0 && *(data->NC) == 0)
				{
					sem_post(data->decision);
				}
				
				sem_wait(data->decision);
			}
			
			if(*(data->NE) == *(data->NC))
			{
				sem_post(data->writer);
			} 

			while(*(data->NE) != *(data->NC))
			{
				sem_wait(data->decision);
			}

			sem_wait(data->writer);
			fprintf(file,"%d : JUDGE : starts confirmation : %d : %d : %d\n", *(data->action), *(data->NE), *(data->NC), *(data->NB));
			*(data->action) = *(data->action) + 1;
			sem_post(data->writer);

			if (strtol(argv[5], NULL, 10) != 0)
			{
				usleep(IntRandom(0, 1000 * strtol(argv[5], NULL, 10)));
			}

			sem_wait(data->writer);
			total = total + *(data->NC);
			*(data->cer) = *(data->cer) + *(data->NC);
			if((*(data->cer) != 0) && (*(data->NC) != 0))
			{
				sem_post(data->certificates);
			}
			*(data->NC) = 0;
			*(data->NE) = 0;
			fprintf(file,"%d : JUDGE : ends confirmation : %d : %d : %d\n", *(data->action), *(data->NE), *(data->NC), *(data->NB));
			*(data->action) = *(data->action) + 1;
			sem_post(data->writer);

			if (strtol(argv[5], NULL, 10) != 0)
			{
				usleep(IntRandom(0, 1000 * strtol(argv[5], NULL, 10)));
			}

			sem_wait(data->writer);
			fprintf(file,"%d : JUDGE : leaves : %d : %d : %d\n", *(data->action), *(data->NE), *(data->NC), *(data->NB));
			*(data->action) = *(data->action) + 1;
			sem_post(data->writer);
			sem_post(data->blocker);
		}

		sem_wait(data->writer);
		fprintf(file,"%d : JUDGE : finishes\n", *(data->action));
		*(data->action) = *(data->action) + 1;
		sem_post(data->writer);

		fclose(file);
		ErrnoExit(data);
		exit(0);
	}

	for(i=0; i < 2; i++) //Hlavny proces caka na podproces sudcu a generator imigrantov.
	{
		wait(NULL);
		if(errno)
		{
			fclose(file);
			ErrnoExit(data);
			fprintf(stderr,"Error, errno was set, on line 349, wait\n");
			return 1;
		}
	}

	fclose(file);
	ErrnoExit(data);
	return 0;
}