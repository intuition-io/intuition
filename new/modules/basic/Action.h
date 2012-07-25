#ifndef DEF_ACTION
#define DEF_ACTION

#include "../../Share.cpp"

class Action : public Share {
    public:
        Action(std::string name, std::string conf_f);
        int init();
};

#endif
