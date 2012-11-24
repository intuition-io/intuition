#include "Interface.h"

using namespace std;
using namespace boost::property_tree;

Interface::Interface() {}

int Interface::init(const string &config_f) {
    cout << "[DEBUG] Retrieving data from json configuration file\n";
    ptree pt;
    try {
        read_json(config_f, pt);
        for ( ptree::iterator itRoot = pt.begin(); itRoot != pt.end(); itRoot++ ) {
            if ( itRoot->first == "core" ) {
                ptree ptChild = pt.get_child("core");
                // Useless at this moment
                for ( ptree::iterator itChild = ptChild.begin(); itChild != ptChild.end(); itChild++ )
                    generalConfig_m[itChild->first] = itChild->second.data();
            } else {
                ptree ptChild = pt.get_child(itRoot->first);
                for ( ptree::iterator itChild = ptChild.begin(); itChild != ptChild.end(); itChild++ ) 
                    modulesConfig_m[itRoot->first][itChild->first] = itChild->second.data();
            }
        }
    }
    catch(exception &e) {
        cout << "[!] Error: " << e.what() << "\n";
        return -1;
    }
    return 0;
}

int Interface::generateConfigFile(string module) {
    //Building target file path
    string moduleConfigFile = "./modules/" + module + "/config.json";
    cout << "[DEBUG] Generating module configuration file: " << moduleConfigFile << endl;
    ptree pt;
    try {
        for ( map<string, string>::iterator it = modulesConfig_m[module].begin(); it != modulesConfig_m[module].end(); it++ ) 
            pt.put(it->first, it->second);
        write_json(moduleConfigFile, pt);
    }
    catch(exception &e) {
        cout << "[!] Error: " << e.what() << "\n";
        return -1;
    }
    return 0;
}

int Interface::process(string module) {
    //TODO Handling multiple modules and informations through generalConfig between them
    //TODO Multithreadé la bête
    int value_r(-2);
    string module_cmd;
    module_cmd = "./modules/" + module + "/" + module;
    cout << "[DEBUG] Checking if processor is available...\n";
    if ( system( NULL ) ) {
        cout << "[DEBUG] OK - Processing " << module << " module: " << module_cmd << "\n";
        value_r = system( module_cmd.c_str() );
        cout << "[DEBUG] Process return value: " << value_r << "\n";
    }
    else
        value_r = -1;
    return value_r;
}
