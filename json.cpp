#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/foreach.hpp>
#include <string>
#include <set>
#include <exception>
#include <iostream>

using namespace boost::property_tree;

struct debug_settings {
    std::string file_m;
    int level_m;
    std::set<std::string> modules_m;
    void load(const std::string &filename);
    void save(const std::string &filename);
};

void debug_settings::load (const std::string &filename) {
    ptree pt;
    read_json(filename, pt);
    file_m = pt.get<std::string>("debug.filename");
    level_m = pt.get("debug.level", 0);
    ptree pt_child = pt.get_child("debug.modules");
    for ( ptree::iterator iptree = pt_child.begin(); iptree != pt_child.end(); iptree++ )
        std::cout << iptree->first << "\n";
}

void debug_settings::save (const std::string &filename) {
    ptree pt;
    pt.put("debug.filename", file_m);
    pt.put("debug.level", level_m);
    pt.put("commande", 42);
    pt.put("node.node_deux.node_trois", "prout");
    write_json(filename, pt);
}

int main() {
    try {
        debug_settings ds;
        ds.load("debug_settings.json");
        ds.save("debug_settings_out.json");
        std::cout << "Success\n";
    }
    catch (std::exception &e) {
        std::cout << "Error: " << e.what() << "\n";
    }
    return 0;
}

