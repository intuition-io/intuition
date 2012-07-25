#ifndef DEF_INTERFACE
#define DEF_INTERFACE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <exception>
#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <sqlite3.h>

class Interface {
    public:
        Interface();
        Interface(std::string index_f, std::string database);
        ~Interface();
        int init(const std::string &config_f);
        void process();
        std::string getTextData(std::string database, std::string table, std::string field, std::string pattern);
        float getRealData(std::string database, std::string table, std::string field, std::string pattern);
        //TODO generateReport() at the end of execution

    private:
        std::string const database_m;
        std::vector<std::string> cmd_m;
        std::string const index_f_m;
        std::string stock_m[6];
        std::map<std::string, std::string> parameters_m;
};

#endif
