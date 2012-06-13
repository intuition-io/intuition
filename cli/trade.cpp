#include <iostream>
#include <stdlib.h>
#include "Interface.cpp"

using namespace std;

int main() {
    cout << "--\tFinancial tool\t--" << endl;

    Interface interpreter("./data/index.db", "./data/quotes.ini", "1", "10", "False");
    string cmd_line("");

    cout << "\t > ";
    getline(cin, cmd_line);
    while ( cmd_line.compare("quit") != 0 ) {
        interpreter.cmd_parser(cmd_line);
        cout << "[DEBUG] Generating config file...\n";
        if ( interpreter.config_file_generator() == 0 ) {
            cout << "[DEBUG] Running python downloader...\n";
            system("./downloader/downloader.py -o dl");
            string infos_to_print = interpreter.accessDb();
            cout << infos_to_print << endl;
        }
        else
            cout << "[!] Error while generating config file...\n";
        cout << "\t > ";
        getline(cin, cmd_line);
    }

    cout << "--\tFinished\t--\n";
    return 0;
}

//TODO le téléchargement de nouvelles valeurs se superposent aux anciennes
