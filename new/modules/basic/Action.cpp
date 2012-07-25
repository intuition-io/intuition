#include "Action.h"

using namespace std;
using namespace boost::property_tree;

Action::Action(string name, string conf_f) : Share(name, conf_f) {
}

int Action::init() {
    cout << "[DEBUG] Basic modul initialisation\n";
    ptree pt;
    try {
        read_json(conf_f_m, pt);
        string test = pt.get("compute.command", "NULL");
        cout << "So: " << test << "\n";
    }
    catch(exception &e) {
        cout << "[ERROR] Basic module initialisation: " << e.what() << "\n";
    }
    return 0;
}
