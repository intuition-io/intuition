#include "Interface.h"

using namespace std;
using namespace boost::property_tree;

Interface::Interface() : index_f_m("./data/index.db"), database_m("./data/assets.db") {
}

Interface::Interface(string index_f, string database) : index_f_m(index_f), database_m(database) {}

int Interface::init(const string &config_f) {
    cout << "[DEBUG] Retireving data from json configuration file\n";
    ptree pt;
    try {
        read_json(config_f, pt);
        cmd_m.push_back(pt.get<string>("commande"));
        cmd_m.push_back(pt.get<string>("share.name"));
        //parameters_m["days"] = pt.get("share.days", "1");
        //parameters_m["action"] = pt.get("share.action", "current");
        //parameters_m["precision"] = pt.get("share.precision", "10");
        //parameters_m["rss"] = pt.get("share.rss", "off");
        parameters_m["module"] = pt.get("module.name", "NULL");
    }
    catch(exception &e) {
        cout << "[!] Error: " << e.what() << "\n";
        return -1;
    }
    return 0;
}

int Interface::process() {
    //TODO Handling multiple modules and informations through parameters between them
    int value_r(-2);
    string module_cmd;
    module_cmd = "./modules/" + parameters_m["module"] + "/" + parameters_m["module"];
    cout << "[DEBUG] Checking if processor is available...\n";
    if ( system( NULL ) ) {
        cout << "[DEBUG] OK - Processing " << parameters_m["module"] << " module: " << module_cmd << "\n";
        value_r = system( module_cmd.c_str() );
        cout << "[DEBUG] Process return value: " << value_r << "\n";
    }
    else
        value_r = -1;
    return value_r;
}
