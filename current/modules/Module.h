#ifndef DEF_MODULE
#define DEF_MODULE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>
#include <string>
#include <map>

class Module {
    public:
        Module(std::string name);
        void init(std::string configFile, map<std::string, std::string> &configuration);

    protected:
        std::string moduleName;
};

#endif
