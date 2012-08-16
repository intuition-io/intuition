#ifndef DEF_ACTION
#define DEF_ACTION

#include "../Share.cpp"

typedef struct Basic Basic;
struct Basic
{
    double value;
    double variation;
    std::string beginDate;
    std::string endDate;
};

class Action : public Share {
    public:
        Action(std::string name, std::string conf_f, std::string rscript, std::string pyscript, std::string rulesdb, std::string assetsdb);
        void evaluateResults(std::map<std::string, std::string>);
        void writeResults(std::string out);

    protected:
        Basic results;
};

#endif
