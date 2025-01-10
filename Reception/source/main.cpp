//AlexisWEISS
#include "MicroBit.h"
#define CLECRYPTAGE 0x4C // Clé XOR
MicroBit uBit;

// Variables globales pour stocker les données reçues
int id = 0;
int i = 0;
int delay = 70;

ManagedString fullMessage = ""; // Stocke le message complet reconstitué
int blockCount = 0;             // Compteur de blocs reçus

/*=====================================FONCTIONS===========================================*/

    ManagedString xorEncryptDecrypt(ManagedString blockMessage) {
    ManagedString result;
    for (int i = 0; i < blockMessage.length(); i++) {
        char encryptedChar = blockMessage.charAt(i) ^ CLECRYPTAGE;
        result = result + encryptedChar;
    }
    return result;
    }

    void onData(MicroBitEvent) {
        // Réception d'un bloc de feux par radio
        ManagedString block = uBit.radio.datagram.recv();
        ManagedString uncrypted_block = xorEncryptDecrypt(block);   
        fullMessage = fullMessage + uncrypted_block; // Ajout du bloc au message complet
        blockCount++;

        // Affichage pour le débogage
        uBit.display.scroll("RX BLOCK", delay);
        uBit.display.scroll(uncrypted_block, delay);

        // Vérifiez si tous les blocs sont reçus
        // Exemple ici : Attendez un maximum de 6 blocs ou un bloc contenant "LAST"
        if (blockCount == 6 || uncrypted_block.substring(uncrypted_block.length() - 3, 3) == "END") {
            uBit.display.scroll("RX COMPLETE", delay); // Débogage : Message complet reçu
            uBit.display.scroll(fullMessage, delay);  // Affiche le message complet pour vérification
            ManagedString messageToSend = fullMessage.substring(0, fullMessage.length() - 3);
            uBit.serial.send(messageToSend + "\n"); // Envoi sur le port série
            // Réinitialise les variables pour le prochain message
            fullMessage = "";
            blockCount = 0;
        }
    }

/*=====================================MAIN===========================================*/

    int main()
    {
        // Initialise le runtime de la micro:bit
        uBit.init();

        // Configure le groupe radio (doit être identique à celui de la carte émettrice)
        uBit.radio.setGroup(76); 
        // Écoute les événements de réception radio
        uBit.messageBus.listen(MICROBIT_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM, onData);
        uBit.radio.enable();
        // Configure le port série
        uBit.serial.baud(115200); // Définit la vitesse du port série
        uBit.serial.setTxBufferSize(248); // Définit la taille du tampon TX si nécessaire

        // Boucle principale
        while (1)
            uBit.sleep(100);

    }
