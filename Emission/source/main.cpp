/*Le but de la carte BRD-C-828 est d'émmèttre les données reçu sur son port série à la carte numéro 1 en liaison radio */

#include <MicroBit.h>
#include <stdio.h>

MicroBit uBit;

/*=====================================FONCTIONS===========================================*/



/*void sendInChunks(ManagedString data) {
    int chunkSize = 32; // Taille maximale d'un message radio
    for (int start = 0; start < data.length(); start += chunkSize) {
        ManagedString chunk = data.substring(start, min(start + chunkSize, data.length()));
        uBit.radio.datagram.send(chunk); // Envoi du fragment
        uBit.sleep(50); // Petite pause entre les fragments
    }
}*/

/*=====================================MAIN===========================================*/

int main() {
    int delay = 70;
    uBit.display.scroll("init",delay);
    uBit.init();

    uBit.radio.enable();
    uBit.radio.setGroup(76); // Groupe radio pour éviter les interférences

    uBit.serial.baud(115200);
    uBit.serial.setRxBufferSize(128); // Taille du tampon de réception

    while (true) {
        uBit.display.scroll("waiting", delay);

        // Vérifie s'il y a des données disponibles sur le port série
        if (uBit.serial.isReadable()) {
            uBit.display.scroll("Reading", delay);

            // Lit les données sur le port série
            ManagedString receivedData = uBit.serial.readUntil('\n'); // Lit jusqu'à une nouvelle ligne
            uBit.display.scroll("Stop Reading", delay);
            uBit.display.scroll(receivedData, delay);

            // Initialisation pour vérifier chaque feu
            bool allFiresValid = true; // Indique si tous les feux sont valides
            int start = 0; // Position de début pour parcourir le message

            // Parcourt chaque feu dans le message
            while (start < receivedData.length()) {
                // Recherche de la prochaine parenthèse fermante `)`
                int end = -1;
                for (int i = start; i < receivedData.length(); i++) {
                    if (receivedData.charAt(i) == ')') {
                        end = i;
                        break;
                    }
                }

                // Si aucune parenthèse fermante trouvée
                if (end == -1) {
                    allFiresValid = false;
                    break;
                }

                // Extraire un feu complet
                ManagedString fireData = receivedData.substring(start, end + 1);
                start = end + 1; // Passe au prochain feu

                // Variables pour stocker les données du feu
                int x = 0, y = 0, i = 0, t = 0;

                // Vérifie le format du feu
                if (sscanf(fireData.toCharArray(), "(%d,%d,%d,%d)", &x, &y, &i, &t) != 4) {
                    allFiresValid = false;
                    break; // Si un feu est mal formé, on arrête
                }
            }

            // Si tous les feux sont valides, on envoie le message complet
            if (allFiresValid) {
                uBit.radio.datagram.send(receivedData); // Envoie tout le message
                uBit.display.scroll("TX OK", delay); // Débogage : confirmation d'envoi
            } else {
                uBit.display.scroll("ERR", delay); // Débogage : erreur dans le format
            }
        }

        // Petite pause pour éviter une boucle trop rapide
        uBit.sleep(100);
        printf("pause de 100ms");
    }



    release_fiber();
}
