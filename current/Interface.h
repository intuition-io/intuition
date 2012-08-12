#ifndef DEF_INTERFACE
#define DEF_INTERFACE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>
#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <cstdlib>
#include <sqlite3.h>

class Interface {
    public:
        Interface();
        int init(const std::string &config_f);
        int generateConfigFile(std::string module);
        int process(std::string module);

    private:
        std::map<std::string, std::string> generalConfig_m;
        std::map<std::string, std::map<std::string, std::string> > modulesConfig_m;
};

#endif
