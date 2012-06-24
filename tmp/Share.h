#ifndef DEF_SHARE
#define DEF_SHARE

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <sqlite3.h>

struct infos_share {
    std::string date;
    std::string hour;
    float value;
    float open;
    int volume;
};

struct stats_share {
    float variation;
};

class Share {
    public:
        Share(std::string name);
        int download(std::string days, std::string precision, std::string action, std::string conf_dl);
        void display();
        int plot();
        std::string getTextData(std::string database, std::string table, std::string field);
        float getRealData(std::string database, std::string table, std::string field);

    private:
        std::string const database;
        std::string const conf_dl;
        std::string const name_m;
        infos_share data_m; 
        stats_share stats_m;
};

#endif
