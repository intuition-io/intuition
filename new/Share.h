#ifndef DEF_SHARE
#define DEF_SHARE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <sqlite3.h>

class Share {
    public:
        Share(std::string name, std::string conf_f);    // DB name is hard coded
        int download(std::string days, std::string precision, std::string action);
        int compute(std::string function);
        std::string getTextData(std::string database, std::string table, std::string field, std::string pattern);
        float getRealData(std::string database, std::string table, std::string field, std::string pattern);

    protected:
        std::string const database_m;
        std::string const conf_f_m;
        std::string const name_m;
};

#endif
