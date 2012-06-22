#ifndef DEF_SHARE
#define DEF_SHARE

#include <fstream>
#include <sstream>
#include <cstdlib>

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
        int download(std::string days, std::string precision, std::string action, std::string conf_f);
        int getData();
        void display();
        int plot();
        int computeVariation(std::string date_from);

    private:
        std::string const index_f_m;
        std::string const data_f_m;
        std::string const name_m;
        infos_share data_m; 
        stats_share stats_m;
};

#endif
