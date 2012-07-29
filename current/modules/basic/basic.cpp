#include <iostream>
#include "Action.cpp"
#include <vector>
#include <string>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>

using namespace std;
using namespace boost::property_tree;

void init(string filename, vector<string> &configuration) {
    ptree pt;
    try {
        read_json(filename, pt);
        //ptree pt_child = pt.get_child("debug.modules");
        for ( ptree::iterator iptree = pt.begin(); iptree != pt.end(); iptree++ )
            //configuration.push_back(iptree->second);
            std::cout << iptree->first << "\n";
    }
    catch(exception &e) {
        cout << "[ERROR] " << e.what() << "\n";
    }
}

int main() {
    cout << "-----------------------------------------------------------------\n";
    cout << "[DEBUG] Module basic running...\n";
    vector<string> configuration;
    init("./modules/basic/config.json", configuration);
    cout << configuration[2] << "  " << configuration[4] << endl;
    return 0;

    Action test("archos", "./modules/basic/config.json");
    if ( test.download("1", "10", "plot") != 0 )
        cout << "[ERROR] downloading\n";
    if ( test.compute("basic") != 0 )
        cout << "[ERROR] computing\n";
    cout << "-----------------------------------------------------------------\n";
    return 0;
}
