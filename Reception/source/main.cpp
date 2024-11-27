//AlexisWEISS
#include "MicroBit.h"

MicroBit uBit;

// Variables globales pour stocker les données reçues
int x = 0;
int y = 0;
int i = 0;
int t = 0;
int delay = 70;

ManagedString fullMessage = ""; // Stocke le message complet reconstitué
int blockCount = 0;             // Compteur de blocs reçus

void onData(MicroBitEvent) {
    // Réception d'un bloc de feux par radio
    ManagedString block = uBit.radio.datagram.recv();
    fullMessage = fullMessage + block; // Ajout du bloc au message complet
    blockCount++;

    // Affichage pour le débogage
    uBit.display.scroll("RX BLOCK", delay);

    // Vérifiez si tous les blocs sont reçus
    // Exemple ici : Attendez un maximum de 6 blocs ou un bloc contenant "LAST"
    if (blockCount == 6 || block.substring(block.length() - 4, block.length()) == "LAST") {
        uBit.display.scroll("RX COMPLETE", delay); // Débogage : Message complet reçu
        uBit.display.scroll(fullMessage, delay);  // Affiche le message complet pour vérification

        // Réinitialise les variables pour le prochain message
        fullMessage = "";
        blockCount = 0;
    }
}



int main()
{
    // Initialise le runtime de la micro:bit
    uBit.init();

    // Configure le groupe radio (doit être identique à celui de la carte émettrice)
    uBit.radio.setGroup(76); 
    // Écoute les événements de réception radio
    uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
    uBit.radio.enable();

    // Boucle principale
    while (1)
        uBit.sleep(1000);

}
