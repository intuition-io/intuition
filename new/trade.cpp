#include <iostream>
#include "Interface.cpp"

using namespace std;

int main() {

#ifdef DEBUG
cout << "[INFO] Debug mode activated\n";
#endif
#ifdef OS_LINUX
cout << "[INFO] Opearting system: Linux\n";
#endif

    /*
     * Crée le noyau manageant la configuration requise
     */
    Interface core("./data/index.db", "./assets.db");

    /*
     *Lecture du fichier de configuration et paramétrage du process
     */
    if ( core.init("./config.json") < 0 )
        cout << "[ERROR] Initializing\n";
    /*
     * Process module execution
     */
    if ( core.process() != 0 )
        cout << "[ERROR] Processing module\n";

    //TODO generateReport()
    //TODO readReport();
    //TODO Envoyer argv[1] ou des saisies d'utilisateur pour influencer le process ?
    return 0;
}
