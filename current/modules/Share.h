#ifndef DEF_SHARE
#define DEF_SHARE

#include <fstream>
#include <sstream>
#include <cstdlib>
#include <map>
#include <vector>
#include <sqlite3.h>

class Share {
    public:
        Share(std::string name, std::string conf_f, std::string rscript, std::string pyscript, std::string rulesdb, std::string assetsdb);
        int download(std::string days, std::string precision, std::string action);
        int compute(std::string function);
        int getTextData(std::vector<std::string> &data, std::string database, std::string table, std::string field, std::string patternField, std::string pattern);
        int getRealData(std::vector<double> &data, std::string database, std::string table, std::string field, std::string patternField, std::string pattern);

    protected:
        std::string const database_m;
        std::string const conf_f_m;
        std::string const name_m;
        std::string const datarules_m;
        std::string const rscript_m;
        std::string const pyscript_m;
};

#endif
