#ifndef DEF_MODULE
#define DEF_MODULE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>
#include <string>
#include <map>
#include <sqlite3.h>

class Module {
    public:
        Module(std::string name);
        void init(std::string configFile, map<std::string, std::string> &configuration);
        std::string getTextData(std::string database, std::string table, std::string field, std::string pattern);
        double getRealData(std::string database, std::string table, std::string field, std::string pattern);

    protected:
        std::string moduleName;
};

#endif
