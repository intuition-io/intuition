#include "Interface.h"

using namespace std;
using namespace boost::property_tree;

Interface::Interface() : index_f_m("./data/index.db") {
}

Interface::Interface(string index_f) : index_f_m(index_f) {}

Interface::~Interface() {
    /*Currently nothing*/
}

int Interface::init(const string &config_f) {
    // Retireving data from json config file
    ptree pt;
    try {
        read_json(config_f, pt);
        cmd_m.push_back(pt.get<string>("commande"));
        cmd_m.push_back(pt.get<string>("share.name"));
        parameters_m["days"] = pt.get("share.days", "1");
        parameters_m["action"] = pt.get("share.action", "current");
        parameters_m["precision"] = pt.get("share.precision", "10");
        parameters_m["rss"] = pt.get("share.rss", "off");
        parameters_m["dependancies"] = pt.get("share.dependancies", "off");
        statistics_m["variation"] = pt.get<string>("stats.variation");
    }
    catch(exception &e) {
        cout << "[!] Error: " << e.what() << "\n";
    }
    if ( parameters_m["dependancies"] == "on" ) {
        cout << "[DEBUG] Storing list of dependancies to handle... ";
        string parent("");
        string child("");
        ifstream flux_in( index_f_m.c_str() );
        string line("");
        while ( getline( flux_in, line ) ) {
            stringstream ss(line);
            ss >> line >> line >> parent >> child;
            if ( parent == cmd_m[1] ) {
                cout << child + ", ";
                cmd_m.push_back(child);
            }
        }
        cout << "Done.\n";
    }
    return 0;
}
 
void Interface::process() {
    for ( vector<string>::iterator it = cmd_m.begin()+1; it != cmd_m.end(); it++ ) {
        cout << "[DEBUG] Processing " << *it << "...\n";
        Share action(*it);
        if ( action.download(parameters_m["days"], parameters_m["precision"], parameters_m["action"]) != 0)
            cout << "[!] Error downloading quotes\n";
        string database("assets.db");
        string table("stocks");
        string field("market");
        string data = action.getTextData(database, table, field);
        cout << data << endl;
    }
}
