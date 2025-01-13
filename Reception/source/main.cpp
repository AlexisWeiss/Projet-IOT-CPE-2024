//AlexisWEISS
#include "MicroBit.h"
#include "aes.hpp"
#include <string.h>
#define CLECRYPTAGE 0x4C // Clé XOR
MicroBit uBit;

// Variables globales pour stocker les données reçues
int id = 0;
int i = 0;
int delay = 50;

ManagedString fullMessage = ""; // Stocke le message complet reconstitué
int blockCount = 0;             // Compteur de blocs reçus

/*=====================================FONCTIONS===========================================*/

static const uint8_t aes_key[16] = {
    0x60, 0x3d, 0xeb, 0x10,
    0x15, 0xca, 0x71, 0xbe,
    0x2b, 0x73, 0xae, 0xf0,
    0x85, 0x7d, 0x77, 0x81
};

int padBuffer(uint8_t* buffer, int length) {
    int paddingLength = 16 - (length % 16);
    for (int i = 0; i < paddingLength; i++) {
        buffer[length + i] = paddingLength;
    }
    return length + paddingLength;
}

ManagedString aesDecrypt(ManagedString data) {
    int dataLen = data.length();
    uint8_t inputBuffer[64];
    memset(inputBuffer, 0, sizeof(inputBuffer));
    memcpy(inputBuffer, data.toCharArray(), dataLen);

    struct AES_ctx ctx;
    AES_init_ctx(&ctx, aes_key);

    for (int i = 0; i < dataLen; i += 16) {
        AES_ECB_decrypt(&ctx, inputBuffer + i);
    }

    int paddingLength = inputBuffer[dataLen - 1];
    int messageLength = dataLen - paddingLength;
    return ManagedString((const char*)inputBuffer, messageLength);
}








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
        ManagedString uncrypted_block = aesDecrypt(block);   
        fullMessage = fullMessage + uncrypted_block; // Ajout du bloc au message complet
        blockCount++;

        // Affichage pour le débogage
        //uBit.display.scroll("RX", delay);
        //uBit.display.scroll(uncrypted_block, delay);

        // Vérifiez si tous les blocs sont reçus
        // Exemple ici : Attendez un maximum de 6 blocs ou un bloc contenant "LAST"
        if (blockCount == 6 || uncrypted_block.substring(uncrypted_block.length() - 3, 3) == "END") {
            //uBit.display.scroll("RXC", delay); // Débogage : Message complet reçu
            //uBit.display.scroll(fullMessage, delay);  // Affiche le message complet pour vérification
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
