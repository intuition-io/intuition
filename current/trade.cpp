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
    Interface core;

    /*
     *Lecture du fichier de configuration et paramétrage du process
     */
    if ( core.init("./config.json") < 0 )
        cout << "** Error initializing\n";

    /*
     * Process module execution
     * Should loop over modules stored from config file
     */
    if ( core.generateConfigFile("basic") < 0 )
        cout << "** Error generating configuration file, module\n";

    if ( core.process("basic") != 0 )
        cout << "** Error processing module\n";

    //TODO generateReport()
    //TODO readReport();
    //TODO Envoyer argv[1] ou des saisies d'utilisateur pour influencer le process ?
    return 0;
}
