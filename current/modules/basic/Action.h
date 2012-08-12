#ifndef DEF_ACTION
#define DEF_ACTION

#include "../Share.cpp"

class Action : public Share {
    public:
        Action(std::string name, std::string conf_f, std::string rscript, std::string pyscript, std::string rulesdb, std::string assetsdb);
};

#endif
