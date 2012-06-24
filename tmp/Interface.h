#ifndef DEF_INTERFACE
#define DEF_INTERFACE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>
#include <string>
#include <vector>
#include <sstream>
#include <map>

class Interface {
    // Methods
    public:
    Interface();
    Interface(std::string index_f);
    ~Interface();
    int init(const std::string &config_f);
    void process();
    //TODO generateReport() at the end of execution

    // Attributes
    private:
    std::vector<std::string> cmd_m;
    std::string const index_f_m;
    std::string stock_m[6];
    std::map<std::string, std::string> parameters_m;
    std::map<std::string, std::string> statistics_m;
};

#endif
