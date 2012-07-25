#include <iostream>
#include "Share.cpp"
#include "Interface.cpp"

using namespace std;

int main() {
    /*
     * Crée le noyau manageant la configuration requise
     */
    Interface core("./data/index.db", "assets.db");

    /*
     *Lecture du fichier de configuration et paramétrage du process
     */
    if ( core.init("./config.json") < 0 )
        cout << "[!] Error initializing\n";
    /*
     *Lance la commande configurée dans l'initialisation
     */
    core.process();
    //TODO Envoyer argv[1] ou des saisies d'utilisateur pour influencer le process ?
    return 0;
}
