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
        Interface(std::string index_f, std::string database);
        int init(const std::string &config_f);
        int process();

    private:
        std::string const database_m;
        std::vector<std::string> cmd_m;
        std::string const index_f_m;
        std::string stock_m[6];
        std::map<std::string, std::string> parameters_m;
};

#endif
