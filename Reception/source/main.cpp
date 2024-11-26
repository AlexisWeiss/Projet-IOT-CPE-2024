#include "MicroBit.h"

MicroBit uBit;

// Variables globales pour stocker les données reçues
int x = 0;
int y = 0;
int i = 0;
int t = 0;

// Fonction appelée lors de la réception des données radio
void onData(MicroBitEvent)
{

    // Réception des données radio
    ManagedString info = uBit.radio.datagram.recv();
    // Analyse de la chaîne reçue
    if (sscanf(info.toCharArray(), "(%d,%d,%d,%d)", &x, &y, &i, &t) == 4) {
        // Affichage des données reçues sur l'écran LED
        ManagedString formattedData = ManagedString("(") + ManagedString(x) + "," + ManagedString(y) + "," + ManagedString(i) + "," + ManagedString(t) + ")";
        uBit.display.scroll(formattedData);
    } else {
        // Affiche une erreur si le format est incorrect
        uBit.display.scroll("ERR");
    }
   /* Backup Chunk
    ManagedString chunk = uBit.radio.datagram.recv();
    ManagedString fullMessage = fullMessage + chunk;

        // Vérifiez si le message est complet (par exemple, se termine par un '}')
        if (fullMessage.charAt(fullMessage.length() - 1) == '}') {
            uBit.display.scroll(fullMessage); // Affichage ou traitement
            fullMessage = ""; // Réinitialiser pour le prochain message
        }

   // Backup Analyse de la chaîne reçue
    if (sscanf(info.toCharArray(), "(%d,%d,%d)", &x, &y, &intensite) == 3) {
        // Affichage des données reçues sur l'écran LED
        ManagedString formattedData = ManagedString("(") + ManagedString(x) + "," + ManagedString(y) + "," + ManagedString(intensite) + ")";
        uBit.display.scroll(formattedData);
    } else {
        // Affiche une erreur si le format est incorrect
        uBit.display.scroll("ERR");
    }*/
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
