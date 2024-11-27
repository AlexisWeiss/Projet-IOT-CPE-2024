/*Le but de la carte BRD-C-828 est d'émmèttre les données reçu sur son port série à la carte numéro 1 en liaison radio */
//AlexisWEISS
#include <MicroBit.h>
#include <stdio.h>

MicroBit uBit;

/*=====================================FONCTIONS===========================================*/



/*=====================================MAIN===========================================*/

int main() {
    int delay = 60;
    uBit.display.scroll("init",delay);
    uBit.init();

    uBit.radio.enable();
    uBit.radio.setGroup(76); // Groupe radio pour éviter les interférences

    uBit.serial.baud(115200);
    uBit.serial.setRxBufferSize(248); // Taille du tampon de réception

        while (true) {
            uBit.display.scroll("waiting", delay);

            // Vérifie s'il y a des données disponibles sur le port série
            if (uBit.serial.isReadable()) {
                uBit.display.scroll("Reading", delay);

                // Lit les données sur le port série
                ManagedString receivedData = uBit.serial.readUntil('\n'); // Lit jusqu'à une nouvelle ligne
                uBit.display.scroll("Stop Reading", delay);
                uBit.display.scroll(receivedData, delay);

                int start = 0;               // Position de début pour parcourir le message (numero de capteur)
                int fireCount = 0;           // Compte le nombre de feux dans un bloc
                ManagedString blockMessage="";  // Stocke les feux dans un bloc de 10 pour envoi radio
                bool isLast = false;         // Indique si le dernier bloc est atteint
                uBit.display.scroll(receivedData.length(), delay);

                // Parcourt chaque feu dans le message
                while (start < receivedData.length()) {
                    int end = start;
                    for (int i = start; i < receivedData.length(); i++) {
                        if (receivedData.charAt(i) == ')') {
                            end = i;
                            break;
                        }
                    }

                    // Si aucune parenthèse fermante trouvée
                    if (end == start) break;

                    // Extraire un feu complet

                    ManagedString fireData = receivedData.substring(start, end+1-start);
                    start = end + 1; // Passe au prochain feu

                    // Variables pour stocker les données du feu
                    int x = 0, y = 0, i = 0, t = 0;

                    // Vérifie le format du feu
                    if (sscanf(fireData.toCharArray(), "(%d,%d,%d,%d)", &x, &y, &i, &t) == 4) {
                        // Ajoute le feu au bloc
                        blockMessage = blockMessage + fireData;
                        fireCount++;
                    } else {
                        // Si un feu est mal formé, afficher une erreur et ignorer ce feu
                        uBit.display.scroll("ERR FIRE", delay);
                        continue;
                    }

                    // Vérifie si on a atteint le dernier feu
                    isLast = (start >= receivedData.length());
                    uBit.display.scroll(fireCount, delay);

                    // Si le bloc contient 10 feux, l'envoyer
                    if (fireCount == 10) {
                        if (isLast) {
                            blockMessage = blockMessage + "LAST"; // Ajoute "LAST" au dernier bloc
                        }
                        uBit.display.scroll(blockMessage, delay);
                        uBit.radio.datagram.send(blockMessage); // Envoi du bloc
                        uBit.display.scroll("TX BLOCK", delay);
                        blockMessage = "";   // Réinitialise le bloc
                        fireCount = 0;       // Réinitialise le compteur
                    }
                    uBit.display.scroll(blockMessage.length(), delay);
                }

                // Envoyer les feux restants dans le dernier bloc (moins de 10 feux)
                if (fireCount > 0) {
                    uBit.display.scroll(blockMessage.length(), delay);
                    blockMessage = blockMessage + "LAST"; // Ajoute LAST à la fin
                    uBit.display.scroll(blockMessage, delay);
                    uBit.radio.datagram.send(blockMessage); // Envoi du dernier bloc
                    uBit.display.scroll("TX LAST", delay);
                    blockMessage = "";   // Réinitialise le bloc
                    fireCount = 0;       // Réinitialise le compteur
                }
            }

        // Petite pause pour éviter une boucle trop rapide
        uBit.sleep(100);
        printf("pause de 100ms");
    }



    release_fiber();
}
