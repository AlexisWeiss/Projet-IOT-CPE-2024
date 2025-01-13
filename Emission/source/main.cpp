/*Le but de la carte BRD-C-828 est d'émmèttre les données reçu sur son port série à la carte numéro 1 en liaison radio */
//Alexis
#include <MicroBit.h>
#include <stdio.h>
#include "aes.hpp"
#include <string.h>
#define CLECRYPTAGE 0x4C // Clé XOR
MicroBit uBit;
int delay = 50;
/*=====================================FONCTIONS===========================================*/

// ClÃ© AES 128 bits (16 octets)
static const uint8_t aes_key[16] = {
    0x60, 0x3d, 0xeb, 0x10,
    0x15, 0xca, 0x71, 0xbe,
    0x2b, 0x73, 0xae, 0xf0,
    0x85, 0x7d, 0x77, 0x81
};

// Fonction de padding PKCS#7
int padBuffer(uint8_t* buffer, int length) {
    int paddingLength = 16 - (length % 16);
    for (int i = 0; i < paddingLength; i++) {
        buffer[length + i] = paddingLength;
    }
    return length + paddingLength;
}

ManagedString aesEncrypt(ManagedString data) {
    int dataLen = data.length();
    const char* c_str = data.toCharArray();

    uint8_t inputBuffer[16];
    memset(inputBuffer, 0, sizeof(inputBuffer));
    memcpy(inputBuffer, c_str, dataLen);

    int paddedLen = padBuffer(inputBuffer, dataLen);

    struct AES_ctx ctx;
    AES_init_ctx(&ctx, aes_key);

    for (int i = 0; i < paddedLen; i += 16) {
        AES_ECB_encrypt(&ctx, inputBuffer + i);
    }

    return ManagedString((const char*)inputBuffer, paddedLen);
}


    bool process_fire(ManagedString fireData, ManagedString &blockMessage, int &fireCount) {
        int id = 0, i = 0;

        // Vérifie le format du feu
        if (sscanf(fireData.toCharArray(), "(%d,%d)", &id, &i) == 2) {
            // Ajoute le feu au bloc
            blockMessage = blockMessage + fireData;
            fireCount++;
            return true; // Feu traité avec succès
        } else {
            // Si un feu est mal formé, afficher une erreur
            uBit.display.scroll("ERR FIRE");
            return false; // Erreur de format
        }
    }

    void send_block_if_full(ManagedString &blockMessage, int &fireCount, bool isLast) { 
        if (fireCount == 10) {
            if (isLast) {
                blockMessage = blockMessage + "END"; // Ajoute "LAST" au dernier bloc
            }
            //uBit.display.scroll(blockMessage, delay);
            uBit.radio.datagram.send(aesEncrypt(blockMessage)); // Envoi du bloc en la cryptant
            //uBit.display.scroll("TX BLOCK", delay);
            blockMessage = "";   // Réinitialise le bloc
            fireCount = 0;       // Réinitialise le compteur
        }
    }

    void send_last_block(ManagedString &blockMessage, int &fireCount) {
        if (fireCount > 0) {
            //uBit.display.scroll(blockMessage.length(), delay); // Affiche la longueur du message pour débogage
            blockMessage = blockMessage + "END";             // Ajoute END à la fin
            //uBit.display.scroll(blockMessage, delay);         // Affiche le message pour débogage
            uBit.radio.datagram.send(aesEncrypt(blockMessage));           // Envoi du bloc en le cryptant
            //uBit.display.scroll("TX", delay);            // Affiche confirmation d’envoi
            blockMessage = "";   // Réinitialise le bloc
            fireCount = 0;       // Réinitialise le compteur
        }
    }



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
                //uBit.display.scroll("w", delay);
                int fireCount = 0;           // Compte le nombre de feux dans un bloc
                ManagedString blockMessage="";  // Stocke les feux dans un bloc de 10 pour envoi radio
                bool isLast = false;         // Indique si le dernier bloc est atteint

                if (uBit.serial.isReadable()) { // Vérifie s'il y a des données disponibles sur le port série

                    //uBit.display.scroll("R", delay);

                    ManagedString receivedData = uBit.serial.readUntil('\n'); // Lit les données sur le port série

                    //uBit.display.scroll("SR", delay);
                    int start = 0;// Position de début pour parcourir le message (numero de capteur)
                    
                    //uBit.display.scroll(receivedData.length(), delay);//DEBUG

                    while (start < receivedData.length()) { // Parcourt chaque feu dans le message

                        int end = start;
                        for (int i = start; i < receivedData.length(); i++) {
                            if (receivedData.charAt(i) == ')') {
                                end = i;
                                break;
                            }
                        }
                        
                        if (end == start) break;// Si aucune parenthèse fermante trouvée

                        ManagedString fireData = receivedData.substring(start, end+1-start);// Extraire un feu complet
                        start = end + 1; // Passe au prochain feu

                        if (!process_fire(fireData, blockMessage, fireCount)) {
                            continue; // Ignore le feu en cas d'erreur
                        }

                        isLast = (start >= receivedData.length());// Vérifie si on a atteint le dernier feu
                        //uBit.display.scroll(fireCount, delay);//DEBUG
                        send_block_if_full(blockMessage, fireCount, isLast);// Si le bloc contient 10 feux, l'envoyer

                    }
                        //uBit.display.scroll(blockMessage.length(), delay);//DEBUG
                }

                // Envoyer les feux restants dans le dernier bloc (moins de 10 feux)
                send_last_block(blockMessage, fireCount);

            }

            // Petite pause pour éviter une boucle trop rapide
            uBit.sleep(100);
        
        release_fiber();
    }
