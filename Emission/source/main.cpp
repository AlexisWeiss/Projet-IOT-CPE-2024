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
            // Variables pour stocker les valeurs extraites
            int x = 0, y = 0, i = 0, t=0;

            // Analyse de la chaîne reçue
            if (sscanf(receivedData.toCharArray(), "(%d,%d,%d,%d)", &x, &y, &i, &t) == 4) {
                // Formatage des données pour l'envoi par radio
                ManagedString formattedData = ManagedString("(") + ManagedString(x) + "," + ManagedString(y) + "," + ManagedString(i) + "," + ManagedString(t) + ")";
                // Envoie les données par radio
                uBit.radio.datagram.send(formattedData);
                // Affiche les données envoyées pour le débogage
                uBit.display.scroll(formattedData);
            } else {
                // Si le format est incorrect, afficher un message d'erreur
                uBit.display.scroll("ERR");
            }
        }

        // Petite pause pour éviter une boucle trop rapide
        uBit.sleep(100);
        printf("pause de 100ms");
    }

    release_fiber();
}
