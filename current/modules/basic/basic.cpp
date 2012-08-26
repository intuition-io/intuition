#include <iostream>
#include "Action.cpp"
#include "../Module.cpp"
#include <map>
#include <vector>
#include <string>


int main(int argc, char** argv) {
    cout << "------- BASIC - MODULE --------------------------------------------------\n";
    cout << "[DEBUG] Module basic running...\n";
    map<string, string> configuration;
    vector<string> deps;
    int stocks(0);
    string configFile;

    Module basic("basic");

    if ( argc > 1 )
        configFile = argv[1];
    else
        configFile = "./modules/basic/config.json";
    basic.init(configFile, configuration);

    Action archos(configuration["name"], configFile, configuration["rscript"], configuration["pyscript"], configuration["rulesdb"], configuration["assetsdb"]);

    //TODO Retrieve market from name
    if ( configuration["dependancies"] == "on" ) {
        cout << "[DEBUG] Handling dependancies, retrieving infos\n";
        stocks = archos.getTextData(deps, configuration["assetsdb"], "stocks", "comment", "ticker", configuration["name"]);
        cout << "Deps on, test: " << deps[0] << endl;
        if ( stocks == 1 ) 
            stocks = archos.getTextData(deps, configuration["assetsdb"], "stocks", "ticker", "comment", deps[0]);
        else
            return 1;
        cout  << "[DEBUG] Actions to process: " << stocks << endl;
    }
    else
        deps.push_back(configuration["name"]);

    //TODO Looping for each asked action or group
    //So accessing database and retrieving a vector through iteration
    for ( int i = 0; i < deps.size(); i++ ) {
        Action archos(deps[i], configFile, configuration["rscript"], configuration["pyscript"], configuration["rulesdb"], configuration["assetsdb"]);
        cout << "[DEBUG] Analysing: " << deps[i] << endl;
        if ( archos.download(configuration["days"], configuration["precision"], "plot") != 0 )
            cout << "** Error downloading\n";
        if ( archos.compute(configuration["command"]) != 0 )
            cout << "** Error computing\n";
        archos.evaluateResults(configuration);
        if ( archos.writeResults(configuration["reportFile"]) < 0 )
            cout << "** Error writting results\n";
    }
    cout << "-------------------------------------------------------------------------\n";
    return 0;
}
