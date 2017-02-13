#include <stdio.h>
#include <arpa/inet.h>

/* 
*  Sérialisation des structures C et compilation:
*
*  Avec "__attribute__ ((__packed__))" 
*  struct msg est déclarée  pour être compilée en 
*  comme non alignée en mémoire : pas de padding pour
*  optimiser l'accès mémoire de la structure par
*  le processeur.

*  Sans cet attribut, struct msg_aligned est implicitement déclarée 
*  avec du padding : le compilateur aligne les données sur
*  la taille des (demi-)registres du processeur cible de la
*  compilation : un champs short, bien que ayant une
*  taille de 16 bits, prendra en réalité 32 bits en 
*  mémoire.
*
*  Exécution :
*
*  msg :
    Le magic du message est 0x73747576
    Le type du message est 0x44556677
    Le handle du message est 0x12345678
    L'offset du message est 0x1012
    La longueur du message est 0x10130000

   msg_aligned :
    Le magic du message est 0x73747576
    Le type du message est 0x44556677
    Le handle du message est 0x12345678
    L'offset du message est 0x1012
    La longueur du message est 0x400

*  Explication : on accède à la même zone mémoire (buffer) avec
   struct msg_aligned et avec struct msg. msg est "packed" et
   accède à la mémoire sans alignement par le compilateur. 
   msg_aligned accède à la mémoire par mots de 32 bits. 
   le champs offset de msg_aligned, déclaré en short (16 bits), 
   affiche bien 0x1012 , puis la longueur à 0x400 : il manque 
   deux octets (0x1013) quelque part si on compte 4 octets et
   2 octets par short.
   
   Pour la structure msg, ces deux octets se retrouvent dans
   le champs longueur, décalés de 2 part rapport à ce qu'on attendait...

   Conclusion : Lorsqu'on sérialise des structures C pour faire communiquer
   des processus, il faut toujours s'assurer que le format sérialisé
   est le même des deux cotés de la communication, quelque soit le 
   language ou du processeur utilisé, ce qui est très fastidieux vu
   le nombre de langages et de processeurs différents existants. On
   verra plus tard qu'il existe des moyens plus propres de sérialiser
   des données, que le simple transfert binaire d'une structure.
*/

struct __attribute__ ((__packed__)) msg { 
    int magic;
    int type;
    int handle;
    short offset;
    int length;
};

struct msg_aligned { 
    int magic;
    int type;
    int handle;
    short offset;
    int length;
};

int main(int argc, char *argv[])
{
	int i;
	char buffer[1024] = {0x76,0x75,0x74,0x73,
                         0x44,0x55,0x66,0x77,
                         0x12,0x34,0x56,0x78,
                         0x10,0x12,0x10,0x13,
                         0x00,0x00,0x04,0x00};
    
	printf("msg et msg_aligned pointent sur le début du buffer:\n");
	printf("{");
	for (i=0;i<20;i++)
		printf("0x%x,",buffer[i]);
	printf("}");
	printf("\n");

    struct msg *m;
    m = (struct msg *)buffer;
    printf("msg (packed) :\n");
    printf("\tLe magic du message est 0x%x\n", m->magic);
    printf("\tLe type du message est 0x%x\n", ntohl(m->type));
    printf("\tLe handle du message est 0x%x\n", ntohl(m->handle));
    printf("\tL'offset du message est 0x%x\n", ntohs(m->offset));
    printf("\tLa longueur du message est 0x%x\n", ntohl(m->length));
    
    struct msg_aligned *m2;
    m2 = (struct msg_aligned *)buffer;
    printf("msg_aligned (not packed):\n");
    printf("\tLe magic du message est 0x%x\n", m2->magic);
    printf("\tLe type du message est 0x%x\n", ntohl(m2->type));
    printf("\tLe handle du message est 0x%x\n", ntohl(m2->handle));
    printf("\tL'offset du message est 0x%x\n", ntohs(m2->offset));
    printf("\tLa longueur du message est 0x%x\n", ntohl(m2->length));

}
