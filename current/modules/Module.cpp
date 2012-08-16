#include "Module.h"

using namespace std;
using namespace boost::property_tree;

Module::Module(string name) : moduleName(name) {}

void Module::init(string configFile, map<string, string> &configuration)
{
	cout << "[DEBUG] Initiating module: " << moduleName << endl;;
    ptree pt;
    try {
        read_json(configFile, pt);
        //ptree pt_child = pt.get_child("debug.modules");
        for ( ptree::iterator iptree = pt.begin(); iptree != pt.end(); iptree++ ) {
            configuration[iptree->first] = iptree->second.data();
            //cout << iptree->first << "\t" << iptree->second.data() << endl;
        }
        
    }
    catch(exception &e) {
        cout << "[ERROR] " << e.what() << "\n";
    }
    cout << " Done.\n";
}

