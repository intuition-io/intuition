#include <iostream>
#include "Action.cpp"
#include "../Module.cpp"
#include <map>
#include <string>


int main(int argc, char** argv) {
    cout << "------- BASIC - MODULE --------------------------------------------------\n";
    cout << "[DEBUG] Module basic running...\n";
    map<string, string> configuration;
    string configFile;

    Module basic("basic");

    if ( argc > 1 )
        configFile = argv[1];
    else
        configFile = "./modules/basic/config.json";
    basic.init(configFile, configuration);
    return 0;

    //TODO Looping for each asked action or group
    //So accessing database and retrieving a vector through iteration
    Action test(configuration["name"], configFile, configuration["rscript"], configuration["pyscript"], configuration["rulesdb"], configuration["assetsdb"]);
    if ( test.download(configuration["days"], configuration["precision"], "plot") != 0 )
        cout << "[ERROR] downloading\n";
    if ( test.compute(configuration["command"]) != 0 )
        cout << "[ERROR] computing\n";
    cout << "-------------------------------------------------------------------------\n";
    return 0;
}
